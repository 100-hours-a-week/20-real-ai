from app.services.chat_service import generate_chat_response
from app.schemas.chat_schema import ChatRequest, ChatResponse

async def chat_response(request: ChatRequest) -> ChatResponse:
    answer = await generate_chat_response(request.question)
    return ChatResponse(answer=answer)