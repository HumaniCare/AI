import os
from datetime import datetime
import io
from pydub import AudioSegment


def merge_all_wavs_to_mp3(audio_dir="audio", silence_duration_ms=500):
    wav_files = sorted([
        os.path.join(audio_dir, f) for f in os.listdir(audio_dir)
        if f.endswith(".wav")
    ])

    if not wav_files:
        print("병합할 .wav 파일이 없습니다.")
        return None

    print(f"{len(wav_files)}개의 wav 파일을 병합 중...")

    combined = AudioSegment.empty()
    silence = AudioSegment.silent(duration=silence_duration_ms)

    for i, wav in enumerate(wav_files):
        audio = AudioSegment.from_wav(wav)
        combined += audio
        if i != len(wav_files) - 1:
            combined += silence  # 마지막 파일 뒤에는 무음 안 넣음

    today_str = datetime.now().strftime("%Y%m%d")
    mp3_path = os.path.join(audio_dir, f"{today_str}_final.mp3")

    combined.export(mp3_path, format="mp3")

    for wav in wav_files:
        os.remove(wav)

    print(f"최종 mp3 저장 완료: {mp3_path}")
    return mp3_path


def convert_to_mp3(file_path):
    audio = AudioSegment.from_file(file_path)
    output_path = file_path.replace(".wav", ".mp3")
    os.remove(file_path)
    audio.export(output_path, format="mp3")
    return output_path


def convert_to_wav(raw_bytes: bytes, file_ext: str) -> bytes:
    # raw_bytes를 파일처럼 다루기 위해 BytesIO로 감싼다.
    bytes_io = io.BytesIO(raw_bytes)
    audio = AudioSegment.from_file(bytes_io, format=file_ext)
    # 원하는 포맷(16kHz mono PCM)으로 변환
    audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
    # WAV 바이트로 내보내기
    out_io = io.BytesIO()
    audio.export(out_io, format="wav")
    return out_io.getvalue()
