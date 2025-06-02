import io
import os
import tempfile
from datetime import datetime

from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError


def merge_all_wavs_to_mp3(audio_dir="audio", silence_duration_ms=500):
    wav_files = sorted([
        os.path.join(audio_dir, f) for f in os.listdir(audio_dir)
        if f.endswith(".wav")
    ])

    if not wav_files:
        print("병합할 .wav 파일이 없습니다.")
        return None

    print(f"{len(wav_files)}개의 wav 파일을 병합 중...")

    combined = AudioSegment.empty()
    silence = AudioSegment.silent(duration=silence_duration_ms)

    for i, wav in enumerate(wav_files):
        audio = AudioSegment.from_wav(wav)
        combined += audio
        if i != len(wav_files) - 1:
            combined += silence  # 마지막 파일 뒤에는 무음 안 넣음

    today_str = datetime.now().strftime("%Y%m%d")
    mp3_path = os.path.join(audio_dir, f"{today_str}_final.mp3")

    combined.export(mp3_path, format="mp3")

    for wav in wav_files:
        os.remove(wav)

    print(f"최종 mp3 저장 완료: {mp3_path}")
    return mp3_path


def convert_to_mp3(file_path):
    audio = AudioSegment.from_file(file_path)
    output_path = file_path.replace(".wav", ".mp3")
    os.remove(file_path)
    audio.export(output_path, format="mp3")
    return output_path


def convert_to_wav(raw_bytes: bytes, ext: str) -> bytes:
    ext = ext.lower()
    # 이미 WAV라면 바로 반환
    if ext == "wav":
        return raw_bytes

    # 임시 입력 파일 생성
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as fin:
        fin.write(raw_bytes)
        fin.flush()
        fin_path = fin.name

    try:
        # 1) format 인자 없이 자동 감지 시도
        audio = AudioSegment.from_file(fin_path)
    except CouldntDecodeError:
        try:
            # 2) 자동 감지도 실패하면, 프로브 크기 늘려서 재시도
            audio = AudioSegment.from_file(
                fin_path,
                parameters=["-probesize", "50M", "-analyzeduration", "100M"]
            )
        except CouldntDecodeError as e:
            os.unlink(fin_path)
            raise RuntimeError(f"FFmpeg 디코딩 실패({ext}): {e}") from e

    # WAV(PCM) 사양으로 맞춰주기
    audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)

    # 메모리로 WAV 내보내기
    out = io.BytesIO()
    audio.export(out, format="wav")
    wav_bytes = out.getvalue()

    os.unlink(fin_path)
    return wav_bytes

    # 3) 원하는 파라메터로 변환 (16kHz, mono, 16-bit)
    audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)

    # 4) 메모리로 WAV 내보내기
    out = io.BytesIO()
    audio.export(out, format="wav")
    wav_bytes = out.getvalue()

    # 5) 임시 입력 파일 삭제
    os.unlink(fin_path)
    return wav_bytes
