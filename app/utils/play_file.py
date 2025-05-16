import time
from datetime import datetime
import os
import subprocess


def play_at_target_time(target_time: str, local_file_path: str):
    # 현재 시간과 target_time 비교
    current_time = datetime.now().strftime("%H:%M:%S")

    # target_time이 현재 시간보다 크면 대기 (target_time까지 대기)
    while current_time < target_time:
        time.sleep(1)  # 1초마다 시간 확인
        current_time = datetime.now().strftime("%H:%M:%S")

    #블루투스 헤드셋 또는 기본 스피커로 출력
    os.system("pactl list sinks | grep 'bluez_sink'")  # 블루투스 출력 장치 확인
    os.system("pactl set-default-sink `pactl list sinks short | grep bluez_sink | awk '{print $2}'`")  # 기본 출력 변경

    # 스피커를 기본 출력 장치로 설정
    os.system("pactl list sinks | grep 'analog-output'")  # 스피커 장치 확인
    os.system("pactl set-default-sink `pactl list sinks short | grep analog-output | awk '{print $2}'`")  # 기본 출력 변경

    #로컬 파일을 직접 재생
    subprocess.run(["mpg321", local_file_path])

    # window 테스트 용
    # from playsound import playsound
    # from pathlib import Path
    # safe_path = Path(local_file_path).resolve().as_posix()
    # playsound(safe_path)
