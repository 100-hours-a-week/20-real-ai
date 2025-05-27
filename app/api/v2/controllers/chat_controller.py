from fastapi import HTTPException
from app.schemas.chat_schema_v2 import ChatRequest, ChatAnswer, ChatResponse
from app.services.chat_service_v2 import chat_service
import uuid
from langsmith import traceable
from langsmith.run_helpers import get_current_run_tree

@traceable(name="Chat Controller", inputs={"질문": lambda args, kwargs: args[0].question})
async def chat_controller(req: ChatRequest) -> ChatResponse:
    request_id = str(uuid.uuid4())
    user_id = req.user_id
    
    # 질문이 비어있을 경우 400 에러 반환
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="질문 내용이 비어 있습니다.")

    # 챗봇 응답 생성 서비스 호출
    answer = await chat_service(req.question, request_id, user_id)

    run = get_current_run_tree()
    if run:
        run.outputs = {"request_id": request_id}

    # 표준 응답 스키마로 래핑하여 반환
    return ChatResponse(
        message="응답이 완료되었습니다.",
        data=ChatAnswer(answer=answer)
    )