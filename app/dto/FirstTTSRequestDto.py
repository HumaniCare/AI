from typing import List

from pydantic import BaseModel


class FirstTTSRequestDto(BaseModel):
    basic_schedule_id: List[int]
    basic_schedule_text: List[str]
