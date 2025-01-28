from music21 import converter

def mxl_to_midi(mxl_file, output_midi_file):
    print(mxl_file)
    # Конвертирует файл из формата MXL (MusicXML) в MIDI.

    score = converter.parse(mxl_file)

    # Сохраняем в MIDI
    score.write("midi", fp=output_midi_file)

    print(f"Файл {mxl_file} успешно конвертирован в {output_midi_file}")


# Получаем список всех MXL-файлов в текущей папке

# УКАЖИТЕ НОРМАЛЬНО ПУТЬ(пример)
# mxl_file = r"C:\Users\User\PycharmProjects\preproff_audio_project\mxl_files\kuzn5.mxl"
# mxl_to_midi(mxl_file, r"C:\Users\User\PycharmProjects\preproff_audio_project\midi_files\mid.midi")