from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    question: str
    user_id : str
    conversation_id: Optional[str] = None

class ChatAnswer(BaseModel):
    answer: str

class ChatResponse(BaseModel):
    message: str
    data: ChatAnswer