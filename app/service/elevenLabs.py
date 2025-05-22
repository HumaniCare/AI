import os
import uuid

from dotenv import load_dotenv
from elevenlabs import ElevenLabs, VoiceSettings

from s3Service import upload_to_s3

load_dotenv()
client = ElevenLabs(
    api_key=os.getenv("ELEVENLABS_KEY"),
)
yjg_voice_id = os.getenv("YJG_VOICE_ID")


def get_voice():
    response = client.voices.get_all()
    voice_ids = [voice.voice_id for voice in response.voices]  # Voice 객체의 voice_id 속성 사용
    return voice_ids


def delete_voice(voice: str):
    try:
        response = client.voices.delete(voice_id=voice)
        print(f"Deleted voice_id: {voice}")
    except Exception as e:
        print(f"Error deleting voice_id {voice}: {e}")


def delete_all_voice(voices: list):
    for voice in voices:
        delete_voice(voice)


def add_voice(name: str, local_file_paths: list):
    # 파일 경로를 통해 파일 객체 생성
    files = []
    for path in local_file_paths:
        with open(path, 'rb') as audio_file:
            files.append(audio_file.read())  # 파일 내용을 리스트에 저장

    response = client.voices.add(name=name, files=files)
    return response.voice_id


def text_to_speech_file_save_AWS(text: str, voice_id=yjg_voice_id) -> str:
    response = client.text_to_speech.convert(
        voice_id=voice_id,
        output_format="mp3_22050_32",
        text=text,
        model_id="eleven_multilingual_v2",
        # voice_settings=VoiceSettings(
        #     stability=0.3,
        #     similarity_boost=1.0,
        #     style=0.0,
        #     use_speaker_boost=True,
        # ),
    )

    save_file_path = f"{uuid.uuid4()}.mp3"
    with open(save_file_path, "wb") as f:
        for chunk in response:
            if chunk:
                f.write(chunk)
    aws_file_url = upload_to_s3(local_file_path=save_file_path)
    os.remove(save_file_path)

    # delete_voice(voice_id)

    return aws_file_url


def text_to_speech_file(text: str, voice_id=yjg_voice_id) -> str:
    response = client.text_to_speech.convert(
        voice_id=voice_id,
        # output_format="mp3_22050_32",
        text=text,
        model_id="eleven_multilingual_v2",
        # voice_settings=VoiceSettings(
        #     stability=0.3,
        #     similarity_boost=1.0,
        #     style=0.0,
        #     use_speaker_boost=True,
        # ),
    )

    save_file_path = f"{uuid.uuid4()}.wav"
    with open(save_file_path, "wb") as f:
        for chunk in response:
            if chunk:
                f.write(chunk)
    # aws_file_url = upload_to_s3(local_file_path=save_file_path)
    # os.remove(save_file_path)

    # delete_voice(voice_id)

    return save_file_path
