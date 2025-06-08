import os
import subprocess
from datetime import datetime

from faster_whisper import WhisperModel
from openai import OpenAI
from elevenlabs import ElevenLabs
from dotenv import load_dotenv

from app.service.elevenLabs import text_to_speech_file
# 녹음 함수 (arecord 사용) - 수정된 record_respberry.py 참고
from record_respberry import emotion_record

# ==== 공통 설정 ====
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVENLABS_KEY = os.getenv("ELEVENLABS_KEY")

if not OPENAI_API_KEY or not ELEVENLABS_KEY:
    raise RuntimeError(".env 에 OPENAI_API_KEY/ELEVENLABS_KEY 를 설정하세요")

# OpenAI / ElevenLabs 클라이언트
gpt_client = OpenAI(api_key=OPENAI_API_KEY)
tts_client = ElevenLabs(api_key=ELEVENLABS_KEY)

# Whisper 모델 (tiny, CPU, int8)
whisper_model = WhisperModel("tiny", device="cpu", compute_type="int8")
# 종료 키워드 목록
EXIT_KEYWORDS = ["그만", "이제 그만", "종료", "끝낼래", "안녕", "잘 자", "다음에 보자", "나중에 얘기해"]
START_COMMUNICATION = "오늘 좋은 하루 보냈나~~?? 어떻게 지냈어!!"
END_COMMUNICATION = "오늘 이야기 나눠서 좋았어. 푹 쉬고, 또 얘기하자~!"


def interaction(alias: str):
    """
    alias: 사용자 이름 또는 AI가 부르는 별칭 (ex: "홍길동")
    1) alias 인사 → TTS → 재생
    2) 이후 반복: emotion_record → Whisper STT → GPT 질문 생성 → TTS → 재생
    종료는 키워드 또는 Ctrl+C로 가능
    """

    # 1) alias 인사
    greet_text = f"{alias}~~ " + START_COMMUNICATION
    print("👋 인사:", greet_text)
    greet_audio = text_to_speech_file(greet_text)
    subprocess.run(["mpg321", greet_audio], check=True)

    # 대화 이력 초기화
    messages = [
        {"role": "system",
         "content": "너는 다정하고 따뜻한 딸이야. 부모님과 이야기할 때는 애정을 담아 걱정해주고, 자연스럽게 다음 말을 이어가야 해. 반말을 쓰되 너무 건방지지는 않게, 친근하고 편안한 말투로 대화해."},
        {"role": "assistant", "content": greet_text}
    ]

    record_idx = 0
    try:
        while True:
            # 2-1) 감정 녹음
            wav_path = emotion_record(record_idx)
            print(f"[녹음 완료] {wav_path}")
            record_idx += 1

            # 2-2) Whisper STT
            segments, _ = whisper_model.transcribe(wav_path, beam_size=1, language="ko")
            user_text = " ".join(seg.text for seg in segments).strip()
            print("▶ 사용자 음성(텍스트):", user_text or "(인식 안됨)")

            if not user_text:
                print("(음성 인식 실패 → 다시 녹음)")
                continue

            # 종료 키워드 감지
            if any(keyword in user_text for keyword in EXIT_KEYWORDS):
                bye_text = f"{alias}~" + END_COMMUNICATION
                print("종료 의사 감지:", user_text)
                bye_audio = text_to_speech_file(bye_text)
                subprocess.run(["mpg321", bye_audio], check=True)
                break

            # 2-3) GPT-4o 질문 생성
            messages.append({"role": "user", "content": user_text})
            resp = gpt_client.chat.completions.create(
                model="gpt-4o",
                messages=messages
            )
            question = resp.choices[0].message.content.strip()
            print("생성된 질문:", question)

            # 2-4) 대화 이력 업데이트
            messages.append({"role": "assistant", "content": question})

            # 2-5) TTS 변환 및 재생
            tts_path = text_to_speech_file(question)
            print("  (TTS 파일 생성:", tts_path, ")")
            subprocess.run(["mpg321", tts_path], check=True)

    except KeyboardInterrupt:
        print("\n[사용자 종료 요청: Ctrl+C]")
        bye_text = f"{alias}~~ " + END_COMMUNICATION
        bye_audio = text_to_speech_file(bye_text)
        subprocess.run(["mpg321", bye_audio], check=True)
    except Exception as e:
        print("예외 발생:", e)

    print("=== interaction 종료 ===")


if __name__ == "__main__":
    # 스크립트를 직접 실행할 때만 동작
    # alias를 원하는 이름으로 바꿔주세요
    interaction("아빠")
