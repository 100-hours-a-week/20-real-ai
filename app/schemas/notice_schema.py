from pydantic import BaseModel

class NoticeRequest(BaseModel):
    title: str
    content: str

class NoticeData(BaseModel):
    summary: str
    isCompleted: bool

class NoticeResponse(BaseModel):
    message: str
    data: NoticeData