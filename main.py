import subprocess
import os
from music21 import converter
from midi2audio import FluidSynth


class AudioConverter:
    def __init__(self, input_file):
        self.name = '\\'.join(input_file.split('/'))
        print(self.name)
        self.clear_name = self.name.split('.')[0].split('\\')[1]
        self.to_img = r'C:\Users\123\PycharmProjects\preproff_audio_project\\' + self.name
        print(self.to_img)
        self.to_mxl = r'C:\Users\123\PycharmProjects\preproff_audio_project\conv\\'
        self.to_wav = r'C:\Users\123\PycharmProjects\preproff_audio_project\results\\' + self.clear_name + '.wav'
        self.audiveris = r'C:\Users\123\PycharmProjects\preproff_audio_project\Audiveris-5.3.1\Audiveris-5.3.1\bin\Audiveris.bat'
        self.sound_font = r'C:\Users\123\PycharmProjects\preproff_audio_project\soundfonts\\'

    def run_audiveris(self):
        # Команда для запуска Audiveris
        command = [
            self.audiveris,  # Путь к audiveris,
            '-batch',  # Режим пакетной обработки
            '-export',  # Экспорт результатов
            '-output', self.to_mxl,  # Папка для сохранения
            self.to_img  # Входное изображение
        ]

        # Запуск процесса
        subprocess.run(command)

    def mxl_to_wav(self, instrument):
        # Загрузка .mxl файла
        score = converter.parse(self.to_mxl + self.clear_name + '.mxl')

        # Сохранение временного MIDI файла
        midi_path = 'temp.mid'
        score.write('midi', midi_path)

        # Рендеринг MIDI в WAV с помощью FluidSynth
        fs = FluidSynth(self.sound_font + instrument)
        fs.midi_to_audio(midi_path, self.to_wav)

        # Удаление временного MIDI файла
        os.remove(midi_path)
        return self.clear_name + '.wav'
