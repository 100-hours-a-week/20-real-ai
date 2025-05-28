from pydantic import BaseModel

class ChatRequest(BaseModel):
    question: str
    userId : int

class ChatAnswer(BaseModel):
    answer: str

class ChatResponse(BaseModel):
    message: str
    data: ChatAnswer