import os
import wave
from datetime import datetime

import numpy as np
import pyaudio

# === 녹음 설정 ===
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 4096               # 약 0.093초 분량 (4096/44100)
SILENCE_LIMIT = 5          # 5초 연속 침묵이면 녹음 종료
BASE_DIR = "/home/team4/Desktop/capstone/AI/app/emotion_diary"

# 날짜 기반 하위 디렉터리(매일 한 번만 생성)
def _ensure_dir():
    os.makedirs(BASE_DIR, exist_ok=True)

def is_silent(data: bytes, threshold: float = 1000.0) -> bool:
    """
    한 프레임(CHUNK) 크기의 raw PCM data를 받아
    RMS 기준으로 침묵 여부를 판단.
    """
    audio_data = np.frombuffer(data, dtype=np.int16)
    rms = np.sqrt(np.mean(audio_data.astype(np.float32) ** 2))
    # print(f"RMS={rms:.1f}")  # 필요 시 디버그용
    return rms < threshold

def emotion_record(index: int) -> str:
    """
    index: 녹음 파일 구분을 위한 정수 인덱스
    return: 저장된 .wav 파일의 전체 경로
    """
    _ensure_dir()
    date_str = datetime.now().strftime("%Y%m%d")
    filename = f"{date_str}_{index}.wav"
    filepath = os.path.join(BASE_DIR, filename)

    pa = pyaudio.PyAudio()
    # input_device_index 를 지정하지 않으면 ALSA default (=USBMIC) 사용
    stream = pa.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK
    )

    print(f"[녹음 시작] {filename}")
    frames = []
    silent_secs = 0.0

    try:
        while True:
            data = stream.read(CHUNK, exception_on_overflow=False)
            frames.append(data)

            if is_silent(data):
                silent_secs += CHUNK / RATE
            else:
                silent_secs = 0.0

            if silent_secs >= SILENCE_LIMIT:
                print(f"[침묵 {SILENCE_LIMIT}초 감지 → 녹음 종료]")
                break

    except Exception as e:
        print("녹음 중 예외:", e)
    finally:
        stream.stop_stream()
        stream.close()
        pa.terminate()

    # WAV 파일로 저장
    wf = wave.open(filepath, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(pa.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    print(f"[저장 완료] {filepath}\n")
    return filepath

