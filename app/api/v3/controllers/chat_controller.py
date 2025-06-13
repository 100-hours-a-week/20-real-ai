from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from app.schemas.chat_schema_v3 import ChatRequest
from app.services.chat_service_v3 import chat_service_stream
import uuid
from langsmith import traceable
from langsmith.run_helpers import get_current_run_tree

async def chat_controller_stream(req: ChatRequest):
    request_id = str(uuid.uuid4())
    userId = req.userId

    # 질문 유효성 검사
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="질문 내용이 비어 있습니다.")

    # chat_service_stream() 호출 → “SSE 이벤트 스트림”
    event_generator = chat_service_stream(req.question, request_id, userId)

    # StreamingResponse 로 반환
    return StreamingResponse(event_generator, media_type="text/event-stream")