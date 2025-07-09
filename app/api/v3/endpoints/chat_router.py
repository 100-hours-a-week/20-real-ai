from fastapi import APIRouter
from app.schemas.chat_schema_v3 import ChatRequest
from app.api.v3.controllers.chat_controller import chat_controller_stream

router = APIRouter()

# 챗봇 질문 응답 API 엔드포인트
@router.post("/chatbots")
async def chat_endpoint(request: ChatRequest):
        # 컨트롤러를 호출하여 응답 생성
        return await chat_controller_stream(request)