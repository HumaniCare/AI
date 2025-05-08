import pyaudio
import wave

from app import convertFileExtension
import sounddevice as sd
import numpy as np
import torch
import time
from scipy.io.wavfile import write
import os
from datetime import datetime
import torchaudio

# 사일로 VAD 모델 불러오기
model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad', model='silero_vad', force_reload=False)
(get_speech_timestamps, save_audio, read_audio, VADIterator, collect_chunks) = utils

SAMPLE_RATE = 16000
FRAME_SIZE = 512
SILENCE_LIMIT = 2.0  # 2초 이상 침묵하면 종료
FILENAME = "output.wav"  # 녹음된 오디오 파일 이름

audio_queue = []
recorded_audio = []


def callback(indata, frames, time_info, status):
    # 받은 오디오 데이터를 audio_queue에 추가
    audio_queue.append(indata[:, 0].copy())


print("Start talking... (녹음 중, 침묵 시 자동 종료)")

with sd.InputStream(callback=callback, channels=1, samplerate=SAMPLE_RATE, blocksize=FRAME_SIZE):
    silence_counter = 0
    while True:
        if len(audio_queue) == 0:
            time.sleep(0.01)
            continue

        chunk = audio_queue.pop(0)
        if len(chunk) < 512:
            continue

        audio_tensor = torch.from_numpy(chunk[:512]).float()
        audio_tensor = audio_tensor / (torch.max(torch.abs(audio_tensor)) + 1e-9)

        speech_prob = model(audio_tensor, SAMPLE_RATE).item()
        print(f"Speech prob: {speech_prob:.3f}")

        # 음성이 인식되었을 때만 녹음
        if speech_prob > 0.5:
            recorded_audio.append(chunk)
            silence_counter = 0  # 음성이 인식되면 침묵 카운터 리셋
        else:
            silence_counter += FRAME_SIZE / SAMPLE_RATE
            print(f"Silence counter: {silence_counter:.2f}")

        # 침묵이 2초 이상 지속되면 녹음 종료
        if silence_counter >= SILENCE_LIMIT:
            print("Silence detected for 2 seconds! Stopping.")
            break

# 녹음된 오디오가 있을 경우에만 파일로 저장

# 저장할 디렉토리 설정
print(os.getcwd())
save_dir = os.path.join(os.getcwd(), "audio")
os.makedirs(save_dir, exist_ok=True)  # 디렉토리가 없으면 생성


# 오늘 날짜 문자열
today_str = datetime.now().strftime("%Y%m%d")
# 파일 이름 설정
FILENAME = "output.wav"
file_path = os.path.join(save_dir, FILENAME)
if recorded_audio:
    recorded_audio = np.concatenate(recorded_audio)

    # 오디오 데이터를 .wav 파일로 저장
    write(file_path, SAMPLE_RATE, recorded_audio.astype(np.float32))  # 저장 형식: .wav
    print(f"녹음된 파일을 {FILENAME}로 저장했습니다.")
else:
    print("녹음된 음성이 없습니다.")





