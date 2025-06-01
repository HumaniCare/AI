import requests
import glob
import os


def predict():
    ip = "10.210.61.102"

    # 서버 URL (라즈베리파이에서 서버 IP와 포트 맞게 수정하세요)
    url = f"http://{ip}:8000/predict"

    # 보낼 wav 파일 경로 리스트 (라즈베리파이 경로)

    BASE_DIR = "/home/team4/Desktop/capstone/AI/app/emotion_diary"
    sample_wav_list = glob.glob(os.path.join(BASE_DIR, "**", "*.wav"), recursive=True)

    files = []
    for i, path in enumerate(sample_wav_list):
        files.append(('files', (f'audio{i}.wav', open(path, 'rb'), 'audio/wav')))

    response = requests.post(url, files=files)

    if response.status_code == 200:
        print("감정 예측 결과:")
        for label, score in response.json().items():
            print(f"{label}: {score}")
    else:
        print(f"Error: {response.status_code} - {response.text}")
