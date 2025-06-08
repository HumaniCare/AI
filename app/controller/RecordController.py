import json
import os
import subprocess
from typing import List

import requests
from boto3 import client
from fastapi import APIRouter, Request, UploadFile, File, Form

from app.dto.ScheduleSpeakRequestDto import ScheduleSpeakRequestDto
from app.dto.ScheduleTTSRequestDto import ScheduleTTSRequestDto
from app.service.elevenLabs import add_voice, text_to_speech_file_save_AWS, text_to_speech_file
from app.service.gpt import ChatgptAPI
from app.service.s3Service import upload_to_s3, download_from_s3, save_local_file
from app.utils import play_file

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
    local_file_path = await save_local_file(file)
    voice_id = add_voice(name="박석진", local_file_paths=[local_file_path])
    voice_url = upload_to_s3(local_file_path)
    os.remove(local_file_path)

    send_user_voice_file_to_spring(token=token, voice_url=voice_url) #yjg_voice_id

#만약 voice_id와 요구하는 분야가 오면 맞춰서 return
@router.post("/schedules")
async def schedule_tts(request: Request, schedules: ScheduleTTSRequestDto):
    # token = request.headers.get("Authorization").split(" ")[1]
    voice_id = yjg_voice_id

    prompt = ChatgptAPI(schedules.schedule_text, "엄마")

    schedule_dict: {"저녁": "엄마~ 저녁 잘 챙겨 먹었어?", "운동": "오늘 운동했어? 건강 챙겨~!"}
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


# @router.post("/basic-tts")
# async def speak_schedule_tts(request: Request, basicTTSRequestDto: BasicTTSRequestDto):
#     # token = request.headers.get("Authorization").split(" ")[1]
#     local_file_path = download_from_s3(basicTTSRequestDto.schedule_voice_Url)
#     print(f"Downloaded file path: {local_file_path}")
#
#     # 블루투스 헤드셋 또는 기본 스피커로 출력
#     os.system("pactl list sinks | grep 'bluez_sink'")  # 블루투스 출력 장치 확인
#     os.system("pactl set-default-sink `pactl list sinks short | grep bluez_sink | awk '{print $2}'`")  # 기본 출력 변경
#
#     # 로컬 파일을 직접 재생
#     subprocess.run(["mpg321", local_file_path])
#
#     return {"message": "TTS completed and played on Bluetooth headset or speaker"}


# @router.post("/extra-tts")
# async def speak_schedule_tts(request: Rlocalhostquest, extraTTSRequestDto: ExtraTTSRequestDto):
#     # token = request.headers.get("Authorization").split(" ")[1]
#     schedule_text = extraTTSRequestDto.schedule_text
#
#     #진짜 실제로 쓸 코드
#     local_file_path = text_to_speech_file(schedule_text, yjg_voice_id)
#
#     # 테스트하면서 AWS에 올려놓으려고 남긴 코드
#     url = text_to_speech_file_save_AWS(schedule_text, yjg_voice_id)
#     local_file_path = download_from_s3(url)
#
#     # local_file_path = os.getcwd()+"/test_audio/test8.mp3" # test
#     # 블루투스 헤드셋 또는 기본 스피커로 출력
#     os.system("pactl list sinks | grep 'bluez_sink'")  # 블루투스 출력 장치 확인
#     os.system("pactl set-default-sink `pactl list sinks short | grep bluez_sink | awk '{print $2}'`")  # 기본 출력 변경
#
#     # 로컬 파일을 직접 재생
#     subprocess.run(["/usr/bin/mpg321", local_file_path])
#     # subprocess.run(["ffplay", "-nodisp", "-autoexit", local_file_path],
#     #                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) # 윈도우용
#     return {"message": "TTS completed and played on Bluetooth headset or speaker"}
#

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


def send_user_speech_file_to_spring(token: str, before_audio_link: str, answerId: int):
    headers = {
        "Authorization": f"Bearer {token}"
    }
    data = {
        "beforeAudioLink": before_audio_link,
        "answerId": answerId
    }
    requests.post("http://springboot:8080/api/spring/records/speeches", headers=headers, json=data)
    # requests.post("https://peachmentor.com/api/spring/records/speeches", headers=headers, json=data)


def receive_self_feedback(token: str) -> str:
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get("http://springboot:8080/api/spring/self-feedbacks/latest-feedbacks", headers=headers)
    # response = requests.get("https://peachmentor.com/api/spring/self-feedbacks/latest-feedbacks", headers=headers)

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
    requests.post("http://springboot:8080/api/spring/statistics", headers=headers, json=data)
    # requests.post("https://peachmentor.com/api/spring/statistics", headers=headers, json=data)

# # 질문 답변에 대한 insight 제공 api
# @router.post("/insights")
# async def getRecord(request: Request, answerId: int = Form(...), question: str = Form(...),
#                     file: UploadFile = File(...)):
#     token = request.headers.get("Authorization").split(" ")[1]
#
#     local_file_path = await s3Service.save_local_file(file)
#     before_audio_link = s3Service.upload_to_s3(local_file_path)
#
#     send_user_speech_file_to_spring(token=token, before_audio_link=before_audio_link, answerId=answerId)
#
#     insightGpt = InsightAssistant(question)
#     insight = insightGpt.get_insight()
#
#     os.remove(local_file_path)
#     return {"insight": insight}


# 피드백 후 데이터 전송 api
# @router.post("/feedbacks")
# async def getFeedback(request: Request, feedbackRequestDto: FeedbackRequestDto):
#     token = request.headers.get("Authorization").split(" ")[1]  # todo: 토큰 에러처리 좀 (밑에도)
#
#     filtered_past_audio_links = [link for link in feedbackRequestDto.pastAudioLinks if
#                                  link != feedbackRequestDto.beforeAudioLink]
#     links = [feedbackRequestDto.beforeAudioLink, feedbackRequestDto.voiceUrl] + filtered_past_audio_links
#     file_paths = download_from_s3_links(links)
#
#     voice_id = add_voice(name=feedbackRequestDto.name, local_file_paths=file_paths)
#
#     transcribe_token = speechToTextWithApi.get_token()
#     t_id = speechToTextWithApi.get_transcribe_id(transcribe_token, beforeAudioLink=feedbackRequestDto.beforeAudioLink)
#
#     time.sleep(0.5)  # 첫 요청시 바로 하면 404 뜰수도 있다고 함
#     first_script, silence_time = speechToTextWithApi.start_stt(transcribe_token, t_id)
#
#     before_script_gpt = FeedbackAssistantUseBeforeScript(first_script)
#     before_script = before_script_gpt.get_feedback()
#
#     filler_count = speechToTextWithApi.get_filler_count(before_script[0])
#
#     feedbackGpt = FeedbackAssistant(first_script, filler_count, silence_time)
#     feedback = feedbackGpt.get_feedback()
#
#     after_audio_link = text_to_speech_file(text=feedback[0], voice_id=voice_id)
#
#     send_statistics_to_spring(token=token, gantourCount=filler_count, silentTime=silence_time,
#                               answerId=feedbackRequestDto.answerId)
#
#     for file_path in file_paths:
#         os.remove(file_path)
#
#     return {"beforeScript": before_script[0],
#             "afterScript": feedback[0],
#             "afterAudioLink": after_audio_link,
#             "feedbackText": "\n".join(feedback[1:])}


# @router.post("/analyses")
# def getUserSpeechHabit(request: Request, analysisRequestDto: AnalysisRequestDto):
#     token = request.headers.get("Authorization").split(" ")[1]
#     analysis_gpt = AnalysisAssistant(questions=analysisRequestDto.questions, beforeScripts=analysisRequestDto.beforeScripts)
#     analysis = analysis_gpt.get_analysis()
#
#     return {"analysisText": analysis}  # 데이터를 JSON 객체로 감쌈