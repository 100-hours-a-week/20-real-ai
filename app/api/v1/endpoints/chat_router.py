from fastapi import APIRouter
from app.schemas.chat_schema import ChatRequest, ChatResponse
from app.api.v1.controllers.chat_controller import chat_controller
from langsmith.run_context import tracing_context

router = APIRouter()

# 챗봇 질문 응답 API 엔드포인트
@router.post("/chatbots", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    with tracing_context(name="ChatBot Session"):
        # 컨트롤러를 호출하여 응답 생성
        return await chat_controller(request)