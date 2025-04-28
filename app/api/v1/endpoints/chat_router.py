from fastapi import APIRouter
from app.schemas.chat_schema import ChatRequest, ChatResponse

router = APIRouter()

@router.post("/chatbots", response_model=ChatResponse, tags=["Chatbot"])
async def get_chatbot_response(request: ChatRequest):
    """
    챗봇 응답 생성 API
    """
    user_message = request.message

    # 간단한 Echo 응답
    response_text = f"네가 보낸 메시지는: {user_message}"

    return ChatResponse(answer=response_text)