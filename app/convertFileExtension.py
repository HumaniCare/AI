import os

from pydub import AudioSegment


def convert_to_mp3(file_path):
    audio = AudioSegment.from_file(file_path)
    output_path = file_path.replace(".wav", ".mp3")
    os.remove(file_path)
    audio.export(output_path, format="mp3")
    return output_path
