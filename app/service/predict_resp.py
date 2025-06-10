import requests
import glob
import os
import mimetypes


def predict():
    # ip = "192.168.1.243"
    ip = "15.165.21.152"
    # FastAPI 라우터 경로에 맞춘 URL
    url = f"http://{ip}:8000/api/fastapi/predict"

    # 전송할 오디오 파일 경로 (wav, m4a, mp3 등 모두 포함)
    BASE_DIR = "/home/team4/Desktop/capstone/AI/app/emotion_diary"
    audio_paths = glob.glob(os.path.join(BASE_DIR, "**", "*.*"), recursive=True)

    files = []
    for path in audio_paths:
        filename = os.path.basename(path)
        # 확장자에 맞는 MIME 타입 추출 (fallback: application/octet-stream)
        content_type = mimetypes.guess_type(path)[0] or "application/octet-stream"
        files.append(
            ("files", (filename, open(path, "rb"), content_type))
        )

    response = requests.post(url, files=files)
    if response.status_code == 200:
        print("감정 예측 결과:")
        for label, score in response.json().items():
            print(f"{label}: {score}")
    else:
        print(f"Error: {response.status_code} - {response.text}")


# if __name__ == "__main__":
#     predict()
