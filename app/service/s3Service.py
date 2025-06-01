import os
import time
import uuid
from typing import List

import requests
from boto3 import client
from botocore.exceptions import ClientError
from dotenv import load_dotenv
from fastapi import UploadFile

from AI.app.utils.convertFileExtension import convert_to_mp3

load_dotenv()

access_key = os.getenv("S3_ACCESSKEY")
secret_key = os.getenv("S3_SECRETKEY")
bucket_name = os.getenv("S3_BUCKET")
url_base = os.getenv("S3_URL")

s3_client = client(
    "s3",
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    region_name="ap-northeast-2",
)


async def save_local_file(file: UploadFile) -> str:
    """업로드된 파일을 로컬에 저장하고 파일 경로를 반환합니다."""
    audio_dir = "./audio"
    if not os.path.exists(audio_dir):
        os.makedirs(audio_dir)
    local_file_path = os.path.join(audio_dir, file.filename)  # 파일 경로 생성
    with open(local_file_path, "wb") as f:
        f.write(await file.read())  # 파일 내용을 저장
    return local_file_path


def upload_to_s3(local_file_path: str) -> str:
    """로컬 파일을 S3에 업로드하고 S3 URL을 반환합니다."""
    try:
        if not os.path.isfile(local_file_path):
            print(f"Local file does not exist: {local_file_path}")
            return None

        timestamp = int(time.time())
        unique_id = str(uuid.uuid4())
        s3_file_name = f"record/audio_{timestamp}_{unique_id}.wav"

        # S3에 파일 업로드
        with open(local_file_path, "rb") as data:
            s3_client.upload_fileobj(data, bucket_name, s3_file_name)

        # S3 URL 생성
        aws_file_url = f"{url_base}/{s3_file_name}"
        return aws_file_url

    except ClientError as e:
        print(f'Credential error => {e}')
    except Exception as e:
        print(f"Another error => {e}")


# AWS S3에서 녹음 파일 다운로드
def download_from_s3(file_s3_url: str) -> str:
    """S3에서 파일을 다운로드하고 로컬에 저장합니다."""
    audio_dir = "./audio"
    if not os.path.exists(audio_dir):
        os.makedirs(audio_dir)  # 디렉토리가 없으면 생성

    try:
        response = requests.get(file_s3_url)
        response.raise_for_status()  # 요청이 실패하면 예외를 발생시킴

        unique_filename = f"{uuid.uuid4()}.wav"
        local_save_path = os.path.join(audio_dir, unique_filename)  # 저장할 파일 경로

        with open(local_save_path, 'wb') as f:
            f.write(response.content)  # 파일 내용을 로컬에 저장

        mp3_file_path = convert_to_mp3(local_save_path)
        return mp3_file_path

    except requests.exceptions.HTTPError as e:
        print(f"HTTP error occurred: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


def download_from_s3_links(urls: List[str]) -> List[str]:
    file_s3_urls = []
    for url in urls:
        file_s3_url = download_from_s3(url)
        file_s3_urls.append(file_s3_url)
    return file_s3_urls


def download_from_s3_model(file_s3_url: str) -> str:
    model_dir = "./model"
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)  # 디렉토리가 없으면 생성

    try:
        response = requests.get(file_s3_url)
        response.raise_for_status()  # 요청이 실패하면 예외를 발생시킴

        unique_filename = str(uuid.uuid4())
        local_save_path = os.path.join(model_dir, unique_filename)  # 저장할 파일 경로

        with open(local_save_path, 'wb') as f:
            f.write(response.content)  # 파일 내용을 로컬에 저장
        return local_save_path

    except requests.exceptions.HTTPError as e:
        print(f"HTTP error occurred: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
