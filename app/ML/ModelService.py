# import numpy as np
# from dotenv import load_dotenv
# from fastapi import Request, UploadFile, File, APIRouter
# from typing import List
# from tensorflow.keras.models import load_model
# from sentence_transformers import SentenceTransformer
# import io
# import requests
#
# from app.ML.audio_extractor_utils import get_features
# from app.ML.loss import boundary_enhanced_focal_loss
# from app.ML.plot_utils import save_plot, get_s3_png_url
# from app.ML.speech_to_text import speech_to_text
#
# import os
#
# from app.service.gpt import EmotionReportGPT
# from app.utils.convertFileExtension import convert_to_wav
#
# router = APIRouter(
#     prefix="/api/fastapi",
# )
# load_dotenv()
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
#
#
#
#
# @router.post("/predict")
# async def predict(request: Request, files: List[UploadFile] = File(...)):
#     # token = request.headers.get("Authorization").split(" ")[1]
#     print(files)
#     # 1) 임시 파일 저장 or 메모리 내 처리
#     wav_data_list = []
#     for file in files:
#         raw = await file.read()
#         ext = file.filename.split('.')[-1]  # 'm4a', 'mp3' 등
#         wav_bytes = convert_to_wav(raw, ext)  # BytesIO 변환
#         wav_data_list.append(wav_bytes)
#
#     # 2) 오디오 특징 추출
#     all_feats = []
#     for wav_bytes in wav_data_list:
#         # get_features 함수가 경로 입력이면, 아래처럼 메모리 파일 처리 필요
#         # 임시파일로 저장 후 경로 전달 or get_features 수정 필요
#
#         temp_path = f"temp_{file.filename}"
#         with open(temp_path, "wb") as f:
#             f.write(wav_bytes)
#         feats = get_features(temp_path)
#         os.remove(temp_path)
#         all_feats.append(feats)
#
#     all_feats = np.stack(all_feats, axis=0)
#     pooled_feats = all_feats.mean(axis=0)
#     audio_input = pooled_feats[np.newaxis, :, np.newaxis]
#
#     # 3) STT & 텍스트 임베딩
#     texts = []
#     for wav_bytes in wav_data_list:
#         temp_path = f"temp_stt.wav"
#         with open(temp_path, "wb") as f:
#             f.write(wav_bytes)
#         text = speech_to_text(temp_path)
#         os.remove(temp_path)
#         texts.append(text)
#
#     full_text = " . ".join(texts)
#     text_vec = embedding_model.encode([full_text])[0]
#     text_input = text_vec[np.newaxis, :]
#
#     # 4) 예측
#     prediction = model.predict([audio_input, text_input])
#     pred_percent = (prediction[0] * 100).tolist()
#
#     # 5) JSON 응답
#     result = {label: round(p, 2) for label, p in zip(emotion_labels, pred_percent)}
#     top_idx = np.argmax(pred_percent)
#     result['predicted_emotion'] = emotion_labels[top_idx]
#
#     local_path = save_plot(pred_percent)
#     s3_path = get_s3_png_url(local_path)
#     reporter = EmotionReportGPT(full_text, pred_percent)
#     report_text = reporter.get_report_text()
#
#     print(s3_path)
#
#     # send_emotion_report_to_spring(s3_path, report_text)
#
#     data = {
#         "imageUrl": s3_path,
#         "report_text": report_text
#     }
#     return data
#
#
#
