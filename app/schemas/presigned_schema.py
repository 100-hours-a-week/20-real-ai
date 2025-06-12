from pydantic import BaseModel

class PresignedRequest(BaseModel):
    title: str
    content: str

class PresignedData(BaseModel):
    fileName: str
    contentType: str
    uuid: str

class PresignedResponse(BaseModel):
    message: str
    data: PresignedData