from typing import List

from pydantic import BaseModel


class BasicTTSRequestDto(BaseModel):
    basic_schedule_id: int
    schedule_voice_Url: str # AWS 저장은 basic schedule 저장시 같이 콜 날라간다고 가정
    target_time: str  # "10:00:00" 형식

