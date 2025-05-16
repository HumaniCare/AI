import pyaudio
import wave
import numpy as np
import os
from datetime import datetime

MIC_INDEX = 1  # USB 마이크 인덱스
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 4096
SILENCE_LIMIT = 5  # 침묵 3초 이상이면 종료

# 오늘 날짜 문자열
today_str = datetime.now().strftime("%Y%m%d")
WAVE_OUTPUT_FILENAME = "/home/team4/Desktop/capstone/AI/app/emotion_diary/" + today_str + "_output.mp3"

def is_silent(data, threshold=100):
    audio_data = np.frombuffer(data, dtype=np.int16)
    rms = np.sqrt(np.mean(audio_data**2))
    print(f"RMS: {rms}")
    return rms < threshold

def emotion_record():
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True,
                    input_device_index=MIC_INDEX, frames_per_buffer=CHUNK)

    print("녹음 시작...")
    frames = []
    silence_counter = 0
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True,
                    input_device_index=MIC_INDEX, frames_per_buffer=CHUNK)

    print("녹음 시작...")
    frames = []
    silence_counter = 0

    while True:
        data = stream.read(CHUNK)
        frames.append(data)
        if is_silent(data):
            silence_counter += CHUNK / RATE
            print(f"침묵 감지: {silence_counter:.2f}초")
        else:
            silence_counter = 0

        if silence_counter >= SILENCE_LIMIT:
            print(f"{SILENCE_LIMIT}초 이상 침묵 감지! 녹음 종료.")
            break

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    print(f"파일 저장 완료: {WAVE_OUTPUT_FILENAME}")
    while True:
        data = stream.read(CHUNK)
        frames.append(data)
        if is_silent(data):
            silence_counter += CHUNK / RATE
            print(f"침묵 감지: {silence_counter:.2f}초")
        else:
            silence_counter = 0

        if silence_counter >= SILENCE_LIMIT:
            print(f"{SILENCE_LIMIT}초 이상 침묵 감지! 녹음 종료.")
            break

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    print(f"파일 저장 완료: {WAVE_OUTPUT_FILENAME}")



# import pyaudio

# p = pyaudio.PyAudio()

# print("==== 오디오 입력 장치 목록 ====")
# for i in range(p.get_device_count()):
#     info = p.get_device_info_by_index(i)
#     if info['maxInputChannels'] > 0:
#         print(f"[Index {i}] {info['name']}")
#         print(f"  - 입력 채널 수 (maxInputChannels): {info['maxInputChannels']}")
#         print(f"  - 기본 샘플레이트 (defaultSampleRate): {int(info['defaultSampleRate'])} Hz")
#         print("-" * 40)

# p.terminate()