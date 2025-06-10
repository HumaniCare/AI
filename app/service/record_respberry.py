import os
import wave
from datetime import datetime
import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write

# === 녹음 설정 ===
CHANNELS = 1
RATE = 44100
CHUNK_DURATION = 0.1  # 초 단위, 약 100ms
CHUNK = int(RATE * CHUNK_DURATION)
SILENCE_LIMIT = 3  # 5초 연속 침묵이면 녹음 종료
THRESHOLD = 0.0003  # 침묵 판별 기준 (RMS)

BASE_DIR = "/home/team4/Desktop/capstone/AI/app/emotion_diary"


# 날짜 기반 하위 디렉터리(매일 한 번만 생성)
def _ensure_dir():
    os.makedirs(BASE_DIR, exist_ok=True)


def is_silent(data: np.ndarray, threshold: float = THRESHOLD) -> bool:
    rms = np.sqrt(np.mean(data ** 2))
    print(f"RMS: {rms:.5f} (threshold: {threshold})")  # 디버깅 출력
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

    print(f"[녹음 시작] {filename}")

    frames = []
    silent_secs = 0.0

    try:
        with sd.InputStream(samplerate=RATE, channels=CHANNELS, dtype='float32') as stream:
            while True:
                data, _ = stream.read(CHUNK)
                audio_chunk = data[:, 0]  # mono
                frames.append(audio_chunk.copy())

                if is_silent(audio_chunk):
                    silent_secs += CHUNK_DURATION
                else:
                    silent_secs = 0.0

                if silent_secs >= SILENCE_LIMIT:
                    print(f"[침묵 {SILENCE_LIMIT}초 감지 → 녹음 종료]")
                    break

    except Exception as e:
        print("녹음 중 예외:", e)

    # float32 → int16 변환 후 저장
    all_audio = np.concatenate(frames)
    int_audio = np.int16(np.clip(all_audio * 32767, -32768, 32767))

    write(filepath, RATE, int_audio)
    print(f"[저장 완료] {filepath}\n")
    return filepath
