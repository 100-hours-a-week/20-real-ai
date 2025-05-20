from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    question: str
    user_id : str
    conversation_id: Optional[str] = None # 첫 요청 시 에러 방지

class ChatAnswer(BaseModel):
    answer: str

class ChatResponse(BaseModel):
    message: str
    data: ChatAnswer
    conversation_id: str