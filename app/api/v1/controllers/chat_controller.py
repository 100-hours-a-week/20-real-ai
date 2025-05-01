from fastapi import HTTPException
from app.schemas.chat_schema import ChatRequest, ChatAnswer, ChatResponse
from app.services.chat_service import generate_chat_response

async def chat_controller(req: ChatRequest) -> ChatResponse:
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="질문 내용이 비어 있습니다.")

    answer = await generate_chat_response(req.question)
    return ChatResponse(
        message="응답이 완료되었습니다.",
        data=ChatAnswer(answer=answer)
    )