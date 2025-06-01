import os
import subprocess
from datetime import datetime

import pyaudio
import numpy as np
from faster_whisper import WhisperModel
from openai import OpenAI
from elevenLabs import text_to_speech_file
from elevenlabs import ElevenLabs
from dotenv import load_dotenv

# 아래 두 함수는 record_respberry.py 에 구현된 그대로 사용합니다.
# emotion_record(index) → "{prefix}{index}.wav" 파일을 만들어 리턴
# is_silent(data) → 음성 청크가 침묵인지 여부 판단
from record_respberry import emotion_record, is_silent

# ==== 공통 설정 ====
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVENLABS_KEY   = os.getenv("ELEVENLABS_KEY")

if not OPENAI_API_KEY or not ELEVENLABS_KEY:
    raise RuntimeError(".env 에 OPENAI_API_KEY/ELEVENLABS_KEY 를 설정하세요")

# OpenAI / ElevenLabs 클라이언트
gpt_client   = OpenAI(api_key=OPENAI_API_KEY)
tts_client   = ElevenLabs(api_key=ELEVENLABS_KEY)

# Whisper 모델 (tiny, CPU, int8)
whisper_model = WhisperModel("tiny", device="cpu", compute_type="int8")

# 녹음 파라미터 (ALSA default=USBMIC 으로 잡힌 상태)
FORMAT   = pyaudio.paInt16
CHANNELS = 1
RATE     = 44100
CHUNK    = RATE * 3    # 3초 단위 버퍼

# 오늘 날짜 기반 녹음 파일 저장 경로 prefix
today_str           = datetime.now().strftime("%Y%m%d")
WAVE_OUTPUT_PREFIX  = f"/home/team4/Desktop/capstone/AI/app/emotion_diary/{today_str}_"

def interaction(alias: str):
    """
    alias: 사용자 이름 또는 AI가 부르는 별칭 (ex: "홍길동")
    1) alias 인사 → TTS → 재생
    2) 이후 반복: emotion_record → Whisper STT → GPT 질문 생성 → TTS → 재생
    """
    # 1) alias 인사
    greet_text = f"{alias}~~ 오늘 좋은 하루 보냈나~~?? 어떻게 지냈어!!"
    print("👋 인사:", greet_text)
    greet_audio = text_to_speech_file(greet_text)
    subprocess.run(["mpg321", greet_audio], check=True)

    # 대화 이력 초기화
    messages = [
        {"role": "system",
         "content": "너는 대화를 자연스럽게 이어가는 AI야. 사용자와 계속 이어지는 대화를 만들어야 해."},
        {"role": "assistant", "content": greet_text}
    ]

    record_idx = 0
    try:
        while True:
            # 2-1) 감정 녹음 (침묵 기준으로 자동 종료)
            wav_path = emotion_record(record_idx)
            print(f"[녹음 완료] {wav_path}")
            record_idx += 1

            # 2-2) Whisper STT (한국어)
            segments, _ = whisper_model.transcribe(wav_path,
                                                   beam_size=1,
                                                   language="ko")
            user_text = " ".join(seg.text for seg in segments).strip()
            print("▶ 사용자 음성(텍스트):", user_text or "(인식 안됨)")

            if not user_text:
                print("(음성 인식 실패 → 다시 녹음)")
                continue

            # 2-3) GPT-4o 에 질문 생성 요청
            messages.append({"role": "user", "content": user_text})
            resp = gpt_client.chat.completions.create(
                model="gpt-4o",
                messages=messages
            )
            question = resp.choices[0].message.content.strip()
            print("생성된 질문:", question)

            # 2-4) 대화 이력에 어시스턴트 질문 추가
            messages.append({"role": "assistant", "content": question})

            # 2-5) 질문 → ElevenLabs TTS → 파일
            tts_path = text_to_speech_file(question)
            print("  (TTS 파일 생성:", tts_path, ")")

            # 2-6) 재생
            subprocess.run(["mpg321", tts_path], check=True)

    except KeyboardInterrupt:
        print("\n[사용자 종료 요청] interaction을 종료합니다.")
    except Exception as e:
        print("예외 발생:", e)

    print("=== interaction 종료 ===")

if __name__ == "__main__":
    # 스크립트를 직접 실행할 때만 동작
    # alias를 원하는 이름으로 바꿔주세요
    interaction("홍길동")

