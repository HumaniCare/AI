from typing import List

from pydantic import BaseModel


class ScheduleTTSRequestDto(BaseModel):
    voice_id: str
    alias: str
    schedule_id: List[int]
    schedule_text: List[str]
