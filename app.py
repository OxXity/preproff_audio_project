from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import SQLAlchemyError
import zipfile
import mimetypes

from main import AudioConverter

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'supersecretkey'
db = SQLAlchemy(app)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['results'] = 'results/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['TEMP_FOLDER'] = 'temp/'


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f'User({self.email})'


class UserSaves(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(250), nullable=False)
    path = db.Column(db.String(250), nullable=False)
    music_path = db.Column(db.String(250), nullable=True)  # New column for music path

    def __repr__(self):
        return f'UserSaves({self.title}, {self.path}, {self.music_path})'


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
        else:
            try:
                new_user = User(email=email)
                new_user.set_password(password)
                db.session.add(new_user)
                db.session.commit()
                flash('Registration successful', 'success')
                return redirect(url_for('login'))
            except SQLAlchemyError as e:
                db.session.rollback()
                flash(f'Database error: {e}', 'danger')
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            flash('Login successful', 'success')
            session['email'] = email
            return redirect(url_for('profile'))
        else:
            flash('Invalid email or password', 'danger')
    return render_template('login.html')


@app.route('/profile')
def profile():
    if 'email' not in session:
        flash('You need to log in first', 'danger')
        return redirect(url_for('login'))
    return render_template('profile.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'email' not in session:
        flash('You need to log in first', 'danger')
        return redirect(url_for('login'))

    if 'files' not in request.files:
        flash('No file part', 'danger')
        return redirect(url_for('profile'))

    files = request.files.getlist('files')
    title = request.form['title']

    if not files or not title:
        flash('No selected file or title', 'danger')
        return redirect(url_for('profile'))

    email = session['email']
    user = User.query.filter_by(email=email).first()

    music_path = None

    for file in files:
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(url_for('profile'))
        if file:
            filename = file.filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            converter = AudioConverter(file_path)
            converter.run_audiveris()

            music_path = os.path.join(app.config['results'], converter.mxl_to_wav('YM2612_Piano_Soundfont.sf2'))
            try:
                new_path = UserSaves(user_id=user.id, title=title, path=file_path, music_path=music_path)
                db.session.add(new_path)
                db.session.commit()
            except SQLAlchemyError as e:
                db.session.rollback()
                flash(f'Database error: {e}', 'danger')
                return redirect(url_for('profile'))
            except Exception as e:
                flash(f'File upload error: {e}', 'danger')
                return redirect(url_for('profile'))

    flash('Files successfully uploaded', 'success')
    return redirect(url_for('profile'))


@app.route('/upl_files')
def upl_files():
    return render_template('upl_files.html')


@app.route('/uploaded_files')
def uploaded_files():
    if 'email' not in session:
        flash('You need to log in first', 'danger')
        return redirect(url_for('login'))

    email = session['email']
    user = User.query.filter_by(email=email).first()
    user_saves = UserSaves.query.filter_by(user_id=user.id).all()

    return render_template('uploaded_files.html', user_saves=user_saves)


@app.route('/download_images/<int:upload_id>')
def download_images(upload_id):
    user_save = UserSaves.query.get(upload_id)
    if not user_save:
        flash('Upload not found', 'danger')
        return redirect(url_for('profile'))

    image_paths = [user_save.path]  # Assuming each upload has one image path

    temp_folder = app.config['TEMP_FOLDER']
    if not os.path.exists(temp_folder):
        os.makedirs(temp_folder)

    zip_path = os.path.join(temp_folder, f'images_{upload_id}.zip')
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for image_path in image_paths:
            zipf.write(image_path, os.path.basename(image_path))

    return send_from_directory(temp_folder, f'images_{upload_id}.zip', as_attachment=True)


@app.route('/download_music/<int:upload_id>')
def download_music(upload_id):
    user_save = UserSaves.query.get(upload_id)
    if not user_save or not user_save.music_path:
        flash('Music file not found', 'danger')
        return redirect(url_for('profile'))

    music_path = user_save.music_path
    mime_type, _ = mimetypes.guess_type(music_path)
    return send_from_directory(app.config['results'], os.path.basename(music_path), mimetype=mime_type,
                               as_attachment=True)


@app.route('/play_music/<int:upload_id>')
def play_music(upload_id):
    user_save = UserSaves.query.get(upload_id)
    # print(user_save)
    if not user_save or not user_save.music_path:
        flash('Music file not found', 'danger')
        return redirect(url_for('profile'))

    music_path = user_save.music_path
    # print(music_path)
    mime_type, _ = mimetypes.guess_type(music_path)
    print(mime_type)
    return send_from_directory(app.config['results'], os.path.basename(music_path), mimetype=mime_type)


@app.route('/delete_upload/<int:upload_id>', methods=['POST'])
def delete_upload(upload_id):
    if 'email' not in session:
        flash('You need to log in first', 'danger')
        return redirect(url_for('login'))

    user_save = UserSaves.query.get(upload_id)
    if not user_save:
        flash('Upload not found', 'danger')
        return redirect(url_for('uploaded_files'))

    try:
        # Remove the associated files from the filesystem
        if user_save.path and os.path.exists(user_save.path):
            os.remove(user_save.path)
        if user_save.music_path and os.path.exists(user_save.music_path):
            os.remove(user_save.music_path)

        # Delete the record from the database
        db.session.delete(user_save)
        db.session.commit()
        flash('Upload deleted successfully', 'success')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'Database error: {e}', 'danger')
    except Exception as e:
        flash(f'File deletion error: {e}', 'danger')

    return redirect(url_for('uploaded_files'))


if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
