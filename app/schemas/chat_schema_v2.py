from pydantic import BaseModel

class ChatRequest(BaseModel):
    question: str
    userId : str

class ChatAnswer(BaseModel):
    answer: str

class ChatResponse(BaseModel):
    message: str
    data: ChatAnswer