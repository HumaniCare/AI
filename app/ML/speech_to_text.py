import speech_recognition as sr

# sample_wav_path = sample_path + "/sh_sadness_2.wav"


# STT 변환 함수
def speech_to_text(audio_path):
    recognizer = sr.Recognizer()

    # 음성 파일 로드
    with sr.AudioFile(audio_path) as source:
        audio_data = recognizer.record(source)  # 음성 데이터 읽기

    try:
        # 구글 STT API 사용 (무료)
        text = recognizer.recognize_google(audio_data, language="ko-KR")
        return text
    except sr.UnknownValueError:
        return "음성을 인식할 수 없습니다."
    except sr.RequestError:
        return "STT 요청 실패"

#
# # MP3에서 변환한 WAV 파일 입력
# sample_text = speech_to_text(sample_wav_path)
# print("변환된 텍스트:", sample_text)
