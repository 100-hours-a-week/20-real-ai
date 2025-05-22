from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    question: str


class ChatAnswer(BaseModel):
    answer: str

class ChatResponse(BaseModel):
    message: str
    data: ChatAnswer
