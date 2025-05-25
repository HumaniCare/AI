from pydantic import BaseModel


class ScheduleSpeakRequestDto(BaseModel):
    schedule_id: int
    schedule_voice_Url: str
    target_time: str  # "10:00:00" 형식
