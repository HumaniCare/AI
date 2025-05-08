from pydantic import BaseModel


class ExtraTTSRequestDto(BaseModel):
    schedule_id: int
    is_basic_schedule: bool
    schedule_text: str
    target_time: str  # "10:00:00" 형식
