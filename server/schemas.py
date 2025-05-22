from pydantic import BaseModel
from typing import Optional

class TextSegment(BaseModel):
    id: str
    text: str
    lang: str = "en"
    speaker: str = "josh_v1"
    done: Optional[bool] = False

class AudioHeader(BaseModel):
    sample_rate: int
    sample_width: int = 2          # bytes
    channels: int = 1
