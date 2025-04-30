from pydantic import BaseModel
from typing import Optional

class DiscordNewsRequest(BaseModel):
    title: Optional[str] = None  # 선택값
    content: str                # 필수값

class DiscordNewsResponse(BaseModel):
    headline: str
    summary: str