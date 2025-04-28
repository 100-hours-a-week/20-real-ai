from fastapi import FastAPI
from app.api.main import api_router

app = FastAPI(
    title="Internal Chatbot API",
    version="0.1.0",
    description="Chatbot + Notice summarization API server"
)

# 라우터 등록
app.include_router(api_router)

# 기본 루트 엔드포인트
@app.get("/")
async def root():
    return {"message": "Welcome to the Internal Chatbot API!"}