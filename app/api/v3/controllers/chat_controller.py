from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from app.schemas.chat_schema_v3 import ChatRequest
from app.services.chat_service_v3 import chat_service_stream
import uuid
from langsmith import traceable
from langsmith.run_helpers import get_current_run_tree
import json

@traceable(name="Chat Controller V2 (Streaming)", inputs={"질문": lambda args, kwargs: args[0].question})
async def chat_controller_stream(req: ChatRequest):
    request_id = str(uuid.uuid4())
    userId = req.userId

    # 질문 유효성 검사
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="질문 내용이 비어 있습니다.")

    # LangSmith run 트리 가져와 리턴 ID 기록
    run = get_current_run_tree()
    if run:
        run.outputs = {"request_id": request_id}

    # 스트리밍 제너레이터 가져오기
    # → chat_service_stream()은 “토큰/청크 단위” async 제너레이터를 리턴
    token_generator = chat_service_stream(req.question, request_id, userId)

    # 작은 유틸: 단일 청크를 SSE 이벤트(f"data: {{...}}\n\n")로 포매팅
    async def event_streamer():
        async for chunk in token_generator:
            # chunk는 vLLM이 반환한 “문자열 한 덩어리”라고 가정
            # 필요 시 JSON 포맷으로 감싸고 싶다면 아래처럼:
            payload = {"delta": chunk}
            yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
        # 스트리밍 완료를 알리는 이벤트 (optional)
        yield "event: end_of_stream\ndata: {}\n\n"

    # StreamingResponse 반환 (media_type="text/event-stream")
    return StreamingResponse(event_streamer(), media_type="text/event-stream")