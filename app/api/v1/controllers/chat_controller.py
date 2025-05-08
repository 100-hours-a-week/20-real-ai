from fastapi import HTTPException
from app.schemas.chat_schema import ChatRequest, ChatAnswer, ChatResponse
from app.services.chat_service import generate_chat_response

async def chat_controller(req: ChatRequest) -> ChatResponse:
    # 질문이 비어있을 경우 400 에러 반환
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="질문 내용이 비어 있습니다.")

    # 챗봇 응답 생성 서비스 호출
    answer = await generate_chat_response(req.question)

    # 표준 응답 스키마로 래핑하여 반환
    return ChatResponse(
        message="응답이 완료되었습니다.",
        data=ChatAnswer(answer=answer)
    )