import time
import pyaudio
import numpy as np
import soundfile as sf
from faster_whisper import WhisperModel
from openai import OpenAI
import openai
from elevenlabs import play, ElevenLabs
from elevenLabs import text_to_speech_file
from dotenv import load_dotenv
import os
from datetime import datetime

from record_respberry import emotion_record, is_silent
model = WhisperModel("tiny", device="cpu", compute_type="int8")
import subprocess

MIC_INDEX = 1  # USB 마이크 인덱스
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 4096
SILENCE_LIMIT = 10 # 침묵 3초 이상이면 종료

# 오늘 날짜 문자열
today_str = datetime.now().strftime("%Y%m%d")
WAVE_OUTPUT_FILENAME = "/home/team4/Desktop/capstone/AI/app/emotion_diary/" + today_str + "_"

# === 환경 변수/API 키 세팅 ===
load_dotenv()

gpt = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)
cloning = ElevenLabs(
    api_key=os.getenv("ELEVENLABS_KEY"),
)

# === Whisper 모델 로드 (tiny가 가장 가볍고 빠름) ===
model = WhisperModel("tiny", device="cpu", compute_type="int8")

# === 오디오 입력 설정 ===
RATE = 44100
CHANNELS = 1
CHUNK = RATE * 3  # 3초 단위로 STT
FORMAT = pyaudio.paInt16

p = pyaudio.PyAudio()
stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
INDEX = 1

print("실시간 STT + GPT 질문 생성 + ElevenLabs Voice Cloning 시작 (Ctrl+C로 종료)")


messages = [
    {"role": "system", "content": "너는 대화를 자연스럽게 이어가는 AI야. 사용자와 계속 이어지는 대화를 만들어야 해."}
]
INDEX = 0

try:
    while True:
        wav_filename = emotion_record(INDEX)
        INDEX += 1

        # === 2. STT ===
        segments, _ = model.transcribe(wav_filename, beam_size=1, language="ko")
        user_text = " ".join([seg.text for seg in segments]).strip()
        print("STT 결과:", user_text)
        if not user_text:
            print("음성이 인식되지 않았습니다.")
            continue

        # 3. messages에 사용자 발화 추가
        messages.append({"role": "user", "content": user_text})

        # 4. GPT에 전체 메시지 전달
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=messages
        )
        question = response['choices'][0]['message']['content'].strip()
        print("생성된 질문:", question)

        # 5. GPT 응답도 messages에 추가
        messages.append({"role": "assistant", "content": question})

        # 6. ElevenLabs TTS로 변환
        audio_path = text_to_speech_file(question)

        # 7. 음성 재생
        subprocess.run(["mpg321", audio_path])

except KeyboardInterrupt:
    print("종료합니다.")
finally:
    stream.stop_stream()
    stream.close()
    p.terminate()

