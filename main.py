import RPi.GPIO as GPIO
import time
from datetime import datetime

PIR_PIN = 17  # GPIO17 (Multiplexing 보드의 IO17)

def detect_motion():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PIR_PIN, GPIO.IN)

    print("PIR 센서 디버깅 시작 (Ctrl+C 종료)")
    prev_state = None  # 직전 상태 기록

    try:
        while True:
            signal = GPIO.input(PIR_PIN)

            if signal != prev_state:
                # 상태가 바뀐 경우만 로그 출력
                timestamp = datetime.now().strftime("%H:%M:%S")
                state_str = "감지됨 (HIGH)" if signal else " 없음 (LOW)"
                print(f"[{timestamp}] 상태 변경 ▶ {state_str}")
                prev_state = signal

            time.sleep(0.1)  # 빠른 주기로 감지

    except KeyboardInterrupt:
        print("⛔ 종료 중...")
        GPIO.cleanup()

if __name__ == "__main__":
    # uvicorn.run(
    #     app="app.main:app",
    #     host="localhost",
    #     # host="0.0.0.0",
    #     port=8000,
    # )
    detect_motion()

