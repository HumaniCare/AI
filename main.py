import RPi.GPIO as GPIO
import time
import uvicorn

PIR_PIN = 17  # 연결된 GPIO 번호 (Multiplexing 보드에서 OUT → GPIO17)

def detect_motion():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PIR_PIN, GPIO.IN)

    print("PIR 센서 작동 중... (Ctrl+C로 종료)")

    try:
        while True:
            signal = GPIO.input(PIR_PIN)

            if signal == GPIO.HIGH:
                print("🟠 움직임 감지됨! (HIGH)")
            else: 
                print("⚪ 감지 없음 (LOW)")

            time.sleep(5)

    except KeyboardInterrupt:
        print("프로그램 종료 중...")
        GPIO.cleanup()


if __name__ == "__main__":
    # uvicorn.run(
    #     app="app.main:app",
    #     host="localhost",
    #     # host="0.0.0.0",
    #     port=8000,
    # )
    detect_motion()

