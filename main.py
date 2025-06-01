# import RPi.GPIO as GPIO
# import time
# from datetime import datetime

# # ───────────────────────────────
# # PIR 센서 관련
# # ───────────────────────────────
# PIR_PIN = 17  # GPIO17

# def detect_motion():
#     GPIO.setmode(GPIO.BCM)
#     GPIO.setup(PIR_PIN, GPIO.IN)

#     print("PIR 센서 디버깅 시작 (Ctrl+C 종료)")
#     prev_state = None

#     try:
#         while True:
#             signal = GPIO.input(PIR_PIN)

#             if signal != prev_state:
#                 timestamp = datetime.now().strftime("%H:%M:%S")
#                 state_str = "감지됨 (HIGH)" if signal else " 없음 (LOW)"
#                 print(f"[{timestamp}] 상태 변경 ▶ {state_str}")
#                 prev_state = signal

#             time.sleep(0.1)
#     except KeyboardInterrupt:
#         print("⛔ 종료 중...")
#         GPIO.cleanup()


# # ───────────────────────────────
# # DHT11 센서 관련 (5회 재시도 버전)
# # ───────────────────────────────
# import adafruit_dht
# import board

# def read_dht11():
#     print("🌡️ DHT11 센서 측정 시작...")
#     dhtDevice = adafruit_dht.DHT11(board.D4)  # GPIO4 (멀티보드 IO4)

#     for i in range(5):  # 최대 5번 재시도
#         try:
#             print(f"📡 시도 {i + 1} ...")
#             temperature = dhtDevice.temperature
#             humidity = dhtDevice.humidity

#             if temperature is not None and humidity is not None:
#                 print(f"✅ 온도: {temperature}°C")
#                 print(f"✅ 습도: {humidity}%")
#                 break
#             else:
#                 print("⚠️ 센서로부터 데이터를 읽을 수 없습니다.")
#         except RuntimeError as error:
#             print(f"⚠️ 에러 발생: {error.args[0]}")
#         except Exception as error:
#             print(f"❌ 심각한 오류: {error}")
#             break
#         time.sleep(2)  # 재시도 간 간격

#     # 종료 함수는 비활성화 (라이브러리 오류 방지)
#     # dhtDevice.exit()

import uvicorn

# ───────────────────────────────
# 메인 함수
# ───────────────────────────────
if __name__ == "__main__":
    uvicorn.run(
        app="app.service.main:app",
        # host="localhost",
        host="0.0.0.0",
        port=8000,
    )
    # detect_motion()  # PIR 센서 테스트 시 주석 해제
#     read_dht11()        # 현재는 DHT11만 테스트

