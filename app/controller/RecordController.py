import os
import time
from typing import List

import requests

from fastapi import APIRouter, Request, UploadFile, File, Form
from boto3 import client
from app import s3Service


from app.dto.FeedbackRequestDto import FeedbackRequestDto
from app.elevenLabs import add_voice, text_to_speech_file, get_voice, delete_all_voice
from app.s3Service import download_from_s3_links

router = APIRouter(
    prefix="/api/fastapi/records",
)

access_key = os.getenv("S3_ACCESS_KEY")
secret_key = os.getenv("S3_SECRET_KEY")
bucket_name = os.getenv("S3_BUCKET_NAME")
url_base = os.getenv("S3_URL")

s3_client = client(
    "s3",
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    region_name="ap-northeast-2",
)


# 첫 로그인 시 1분 목소리 녹음 api
@router.post("/voices")
async def getVoice(request: Request, file: UploadFile = File(...)):
    token = request.headers.get("Authorization").split(" ")[1]
    local_file_path = await s3Service.save_local_file(file)
    voice_url = s3Service.upload_to_s3(local_file_path)
    os.remove(local_file_path)

    send_user_voice_file_to_spring(token=token, voice_url=voice_url)


# 질문 답변에 대한 insight 제공 api
@router.post("/insights")
async def getRecord(request: Request, answerId: int = Form(...), question: str = Form(...),
                    file: UploadFile = File(...)):
    token = request.headers.get("Authorization").split(" ")[1]

    local_file_path = await s3Service.save_local_file(file)
    before_audio_link = s3Service.upload_to_s3(local_file_path)

    send_user_speech_file_to_spring(token=token, before_audio_link=before_audio_link, answerId=answerId)

    insightGpt = InsightAssistant(question)
    insight = insightGpt.get_insight()

    os.remove(local_file_path)
    return {"insight": insight}


# 피드백 후 데이터 전송 api
@router.post("/feedbacks")
async def getFeedback(request: Request, feedbackRequestDto: FeedbackRequestDto):
    token = request.headers.get("Authorization").split(" ")[1]  # todo: 토큰 에러처리 좀 (밑에도)

    filtered_past_audio_links = [link for link in feedbackRequestDto.pastAudioLinks if
                                 link != feedbackRequestDto.beforeAudioLink]
    links = [feedbackRequestDto.beforeAudioLink, feedbackRequestDto.voiceUrl] + filtered_past_audio_links
    file_paths = download_from_s3_links(links)

    voice_id = add_voice(name=feedbackRequestDto.name, local_file_paths=file_paths)

    transcribe_token = speechToTextWithApi.get_token()
    t_id = speechToTextWithApi.get_transcribe_id(transcribe_token, beforeAudioLink=feedbackRequestDto.beforeAudioLink)

    time.sleep(0.5)  # 첫 요청시 바로 하면 404 뜰수도 있다고 함
    first_script, silence_time = speechToTextWithApi.start_stt(transcribe_token, t_id)

    before_script_gpt = FeedbackAssistantUseBeforeScript(first_script)
    before_script = before_script_gpt.get_feedback()

    filler_count = speechToTextWithApi.get_filler_count(before_script[0])

    feedbackGpt = FeedbackAssistant(first_script, filler_count, silence_time)
    feedback = feedbackGpt.get_feedback()

    after_audio_link = text_to_speech_file(text=feedback[0], voice_id=voice_id)

    send_statistics_to_spring(token=token, gantourCount=filler_count, silentTime=silence_time,
                              answerId=feedbackRequestDto.answerId)

    for file_path in file_paths:
        os.remove(file_path)

    return {"beforeScript": before_script[0],
            "afterScript": feedback[0],
            "afterAudioLink": after_audio_link,
            "feedbackText": "\n".join(feedback[1:])}


@router.post("/analyses")
def getUserSpeechHabit(request: Request, analysisRequestDto: AnalysisRequestDto):
    token = request.headers.get("Authorization").split(" ")[1]
    analysis_gpt = AnalysisAssistant(questions=analysisRequestDto.questions, beforeScripts=analysisRequestDto.beforeScripts)
    analysis = analysis_gpt.get_analysis()

    return {"analysisText": analysis}  # 데이터를 JSON 객체로 감쌈


# past audio 중, 중복되는 before audio 제거
def get_audio_file_paths(feedbackRequestDto: FeedbackRequestDto) -> List[str]:
    filtered_past_audio_links = [link for link in feedbackRequestDto.pastAudioLinks if
                                 link != feedbackRequestDto.beforeAudioLink]
    links = [feedbackRequestDto.beforeAudioLink, feedbackRequestDto.voiceUrl] + filtered_past_audio_links
    return download_from_s3_links(links)


def send_user_voice_file_to_spring(token: str, voice_url: str):
    headers = {
        "Authorization": f"Bearer {token}"
    }
    data = {
        "voiceUrl": voice_url
    }
    # requests.post("http://localhost:8080/api/spring/records/voices", headers=headers, json=data)
    requests.post("https://peachmentor.com/api/spring/records/voices", headers=headers, json=data)


def send_user_speech_file_to_spring(token: str, before_audio_link: str, answerId: int):
    headers = {
        "Authorization": f"Bearer {token}"
    }
    data = {
        "beforeAudioLink": before_audio_link,
        "answerId": answerId
    }
    # requests.post("http://localhost:8080/api/spring/records/speeches", headers=headers, json=data)
    requests.post("https://peachmentor.com/api/spring/records/speeches", headers=headers, json=data)


def receive_self_feedback(token: str) -> str:
    headers = {
        "Authorization": f"Bearer {token}"
    }
    # response = requests.get("http://localhost:8080/api/spring/self-feedbacks/latest-feedbacks", headers=headers)
    response = requests.get("https://peachmentor.com/api/spring/self-feedbacks/latest-feedbacks", headers=headers)

    feedback_data = response.json().get('result', {})
    self_feedback = feedback_data.get('feedback')

    if self_feedback is None:
        return "없음"
    return self_feedback


def send_statistics_to_spring(token: str, gantourCount: int, silentTime: float, answerId: int):
    headers = {
        "Authorization": f"Bearer {token}"
    }
    data = {
        "gantourCount": gantourCount,
        "silentTime": silentTime,
        "answerId": answerId
    }
    # requests.post("http://localhost:8080/api/spring/statistics", headers=headers, json=data)
    requests.post("https://peachmentor.com/api/spring/statistics", headers=headers, json=data)
