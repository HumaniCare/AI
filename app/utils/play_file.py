from datetime import datetime
import subprocess
import time


def play_at_target_time(target_time: str, local_file_path: str):
    # 현재 시간과 target_time 비교
    current_time = datetime.now().strftime("%H:%M:%S")

    # target_time이 현재 시간보다 크면 대기 (target_time까지 대기)
    while current_time != target_time:
        time.sleep(1)  # 1초마다 시간 확인
        current_time = datetime.now().strftime("%H:%M:%S")

    # target_time에 맞춰서 TTS 파일 재생
    subprocess.run(["mpg321", local_file_path])