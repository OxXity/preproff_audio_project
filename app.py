from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import SQLAlchemyError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'supersecretkey'
db = SQLAlchemy(app)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


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

    def __repr__(self):
        return f'UserSaves({self.title}, {self.path})'


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

    for file in files:
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(url_for('profile'))
        if file:
            filename = file.filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            try:
                new_path = UserSaves(user_id=user.id, title=title, path=file_path)
                db.session.add(new_path)
                db.session.commit()
                file.save(file_path)
            except SQLAlchemyError as e:
                db.session.rollback()
                flash(f'Database error: {e}', 'danger')
                return redirect(url_for('profile'))
            except Exception as e:
                flash(f'File upload error: {e}', 'danger')
                return redirect(url_for('profile'))

    flash('Files successfully uploaded', 'success')
    return redirect(url_for('profile'))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
