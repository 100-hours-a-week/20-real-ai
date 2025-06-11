from pydantic import BaseModel

class PresignedRequest(BaseModel):
    title: str
    content: str

class PresignedResponse(BaseModel):
    fileName: str
    contentType: str
    uuid: str