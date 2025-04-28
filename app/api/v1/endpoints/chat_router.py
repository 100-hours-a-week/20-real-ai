from fastapi import APIRouter
from app.schemas.chat_schema import ChatRequest, ChatResponse

router = APIRouter()

@router.post("/chatbots", response_model=ChatResponse, tags=["Chatbot"])
async def get_chatbot_response(request: ChatRequest):
    """
    챗봇 응답 생성 API
    """
    # TODO: 추후 서비스 로직 연결 예정
    return ChatResponse(answer="This is a dummy chatbot response.")