from pydantic import BaseModel

class WikiNewsRequest(BaseModel):
    uuid: str
    presignedUrl: str

class WikiNewsData(BaseModel):
    headline: str
    summary: str
    news: str
    imageUrl: str
    isCompleted: bool

class WikiNewsResponse(BaseModel):
    message: str
    data: WikiNewsData