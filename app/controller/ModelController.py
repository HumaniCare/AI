import numpy as np
from fastapi import FastAPI, UploadFile, File, APIRouter
from typing import List
from tensorflow.keras.models import load_model
from sentence_transformers import SentenceTransformer
import io

from app.ML.audio_extractor_utils import get_features
from app.ML.loss import boundary_enhanced_focal_loss
from app.ML.speech_to_text import speech_to_text

import os

router = APIRouter(
    prefix="/api/fastapi",
)

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# app = FastAPI()

BASE_DIR_win = "C:/Users/YJG/Desktop/2025_1_capstone_2/AI/app/emotion_diary"
model_path_win = "C:/Users/YJG/Desktop/2025_1_capstone_2/AI/app/ML/ko-sbert_multimodal_0501_3_resnet_augment_h.h5"
emotion_labels = ['angry', 'sadness', 'happiness', 'fear', 'disgust', 'surprise', 'neutral']

embedding_model = SentenceTransformer('jhgan/ko-sbert-multitask')
model = load_model(model_path_win, custom_objects={'boundary_enhanced_focal_loss': boundary_enhanced_focal_loss})


@router.post("/predict")
async def predict(files: List[UploadFile] = File(...)):
    # 1) 임시 파일 저장 or 메모리 내 처리
    wav_data_list = []
    for file in files:
        contents = await file.read()
        wav_data_list.append(contents)

    # 2) 오디오 특징 추출
    all_feats = []
    for wav_bytes in wav_data_list:
        # get_features 함수가 경로 입력이면, 아래처럼 메모리 파일 처리 필요
        # 임시파일로 저장 후 경로 전달 or get_features 수정 필요
        # 여기서는 임시파일에 저장 후 경로 넘기는 예제
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

    return result
