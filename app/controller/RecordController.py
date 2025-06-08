import json
import os
import subprocess
from typing import List

import numpy as np
import requests
from boto3 import client
from fastapi import APIRouter, Request, UploadFile, File, Form
# from sentence_transformers import SentenceTransformer

from app.ML.audio_extractor_utils import get_features
from app.ML.loss import boundary_enhanced_focal_loss
from app.ML.plot_utils import save_plot, get_s3_png_url
from app.ML.speech_to_text import speech_to_text
from app.dto.ScheduleSpeakRequestDto import ScheduleSpeakRequestDto
from app.dto.ScheduleTTSRequestDto import ScheduleTTSRequestDto
from app.service.elevenLabs import text_to_speech_file_save_AWS, text_to_speech_file
from app.service.gpt import ChatgptAPI, EmotionReportGPT
from app.service.s3Service import download_from_s3, save_local_file
from app.utils import play_file
from tensorflow.keras.models import load_model

from app.utils.convertFileExtension import convert_to_wav

router = APIRouter(
    prefix="/api/fastapi",
)

access_key = os.getenv("S3_ACCESS_KEY")
secret_key = os.getenv("S3_SECRET_KEY")
bucket_name = os.getenv("S3_BUCKET_NAME")
url_base = os.getenv("S3_URL")
yjg_voice_id = os.getenv("YJG_VOICE_ID")

s3_client = client(
    "s3",
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    region_name="ap-northeast-2",
)

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# app = FastAPI()

BASE_DIR_win = os.getcwd() + "/app/emotion_diary"
model_path_win = os.getcwd() + "/app/ML/ko-sbert_multimodal_0501_3_resnet_augment_h.h5"
emotion_labels = ['angry', 'sadness', 'happiness', 'fear', 'disgust', 'surprise', 'neutral']

embedding_model = SentenceTransformer('jhgan/ko-sbert-multitask')
model = load_model(model_path_win, custom_objects={'boundary_enhanced_focal_loss': boundary_enhanced_focal_loss})


async def save_local_files(files: List[UploadFile]) -> list:
    """업로드된 파일을 로컬에 저장하고 파일 경로를 반환합니다."""
    audio_dir = "./audio"
    local_file_path_list = []
    if not os.path.exists(audio_dir):
        os.makedirs(audio_dir)
    for file in files:
        local_file_path = os.path.join(audio_dir, file.filename)  # 파일 경로 생성
        with open(local_file_path, "wb") as f:
            f.write(await file.read())  # 파일 내용을 저장
        local_file_path_list.append(local_file_path)
    return local_file_path_list


# 첫 로그인 시 목소리 녹음 api
@router.post("/voices")
async def getVoice(request: Request, file: UploadFile = File(...)):
    token = request.headers.get("Authorization").split(" ")[1]
    # local_file_path = await save_local_file(file)
    # voice_id = add_voice(name=name, local_file_paths=[local_file_path])
    # voice_url = s3Service.upload_to_s3(local_file_path)
    # os.remove(local_file_path)

    send_user_voice_file_to_spring(token=token, voice_url=yjg_voice_id)


# 만약 voice_id와 요구하는 분야가 오면 맞춰서 return
@router.post("/schedules")
async def schedule_tts(request: Request, schedules: ScheduleTTSRequestDto):
    # token = request.headers.get("Authorization").split(" ")[1]
    voice_id = yjg_voice_id

    prompt = ChatgptAPI(schedules.schedule_text, schedules.alias)

    # schedule_dict: {"저녁": "엄마~ 저녁 잘 챙겨 먹었어?", "운동": "오늘 운동했어? 건강 챙겨~!"}
    schedule_dict = prompt.get_schedule_json()

    # TTS 처리 (MP3 파일 생성 후 s3 저장)
    response = {
        schedules.schedule_id[i]: text_to_speech_file_save_AWS(
            schedule_dict.get(schedules.schedule_text[i], ""),
            yjg_voice_id
        )
        # schedules.schedule_id[i]: str(schedules.schedule_id[i])
        for i in range(len(schedules.schedule_id))
    }
    return response


@router.post("/predict")
async def predict(request: Request, files: List[UploadFile] = File(...)):
    # token = request.headers.get("Authorization").split(" ")[1]
    print(files)
    # 1) 임시 파일 저장 or 메모리 내 처리
    wav_data_list = []
    for file in files:
        raw = await file.read()
        ext = file.filename.split('.')[-1]  # 'm4a', 'mp3' 등
        wav_bytes = convert_to_wav(raw, ext)  # BytesIO 변환
        wav_data_list.append(wav_bytes)

    # 2) 오디오 특징 추출
    all_feats = []
    for wav_bytes in wav_data_list:
        # get_features 함수가 경로 입력이면, 아래처럼 메모리 파일 처리 필요
        # 임시파일로 저장 후 경로 전달 or get_features 수정 필요

        temp_path = f"temp_{file.filename}"
        with open(temp_path, "wb") as f:
            f.write(wav_bytes)
        feats = get_features(temp_path)
        os.remove(temp_path)
        all_feats.append(feats)

    all_feats = np.stack(all_feats, axis=0)
    pooled_feats = all_feats.mean(axis=0)
    audio_input = pooled_feats[np.newaxis, :, np.newaxis]

    # 3) STT & 텍스트 임베딩
    texts = []
    for wav_bytes in wav_data_list:
        temp_path = f"temp_stt.wav"
        with open(temp_path, "wb") as f:
            f.write(wav_bytes)
        text = speech_to_text(temp_path)
        os.remove(temp_path)
        texts.append(text)

    full_text = " . ".join(texts)
    text_vec = embedding_model.encode([full_text])[0]
    text_input = text_vec[np.newaxis, :]

    # 4) 예측
    prediction = model.predict([audio_input, text_input])
    pred_percent = (prediction[0] * 100).tolist()

    # 5) JSON 응답
    result = {label: round(p, 2) for label, p in zip(emotion_labels, pred_percent)}
    top_idx = np.argmax(pred_percent)
    result['predicted_emotion'] = emotion_labels[top_idx]

    local_path = save_plot(pred_percent)
    s3_path = get_s3_png_url(local_path)
    reporter = EmotionReportGPT(full_text, pred_percent)
    report_text = reporter.get_report_text()

    print(s3_path)

    # send_emotion_report_to_spring(s3_path, report_text)

    data = {
        "imageUrl": s3_path,
        "report_text": report_text
    }
    return data


def send_user_voice_file_to_spring(token: str, voice_url: str):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "text/plain"
    }
    # requests.post("http://localhost:8080/api/spring/records/voices", headers=headers, json=data)
    # requests.post("https://peachmentor.com/api/spring/records/voices", headers=headers, json=data)

    requests.post(
        "http://springboot:8080/api/spring/records/voices",
        headers=headers,
        data=voice_url  # 주의: 'data='를 써야 함
    )


def send_user_voice_id_to_spring(token: str, voice_id: str):
    headers = {
        "Authorization": f"Bearer {token}"
    }
    data = {
        "voiceId": voice_id
    }
    requests.post("http://localhost:8080/api/spring/records/voices", headers=headers, json=data)
    # requests.post("https://peachmentor.com/api/spring/records/voices", headers=headers, json=data)


def send_emotion_report_to_spring(image_url: str, analysis_text):
    headers = {
        # "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "imageUrl": image_url,
        "report_text": analysis_text
    }
    requests.post(
        "http://springboot:8080/api/spring/report",
        headers=headers,
        json=data
    )
