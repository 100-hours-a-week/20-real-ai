from pydantic import BaseModel

class WikiNewsRequest(BaseModel):
    title: str
    content: str

class WikiNewsData(BaseModel):
    headline: str
    summary: str
    content: str
    image_url: str
    isCompleted: bool

class WikiNewsResponse(BaseModel):
    message: str
    data: WikiNewsData