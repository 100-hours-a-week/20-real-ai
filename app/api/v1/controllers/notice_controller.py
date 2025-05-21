from app.services.notice_service import summarize_notice_service
from app.schemas.notice_schema import NoticeRequest, NoticeResponse, NoticeData
import uuid
from langsmith import traceable

@traceable(name="Notice Controller", inputs={"제목": lambda args, kwargs: args[0].title, "본문": lambda args, kwargs: args[0].content})
async def summarize_notice(request: NoticeRequest) -> NoticeResponse:
    request_id = str(uuid.uuid4())

    summary, isCompleted = await summarize_notice_service(request.title, request.content, request_id)

    return NoticeResponse(
        message="공지사항 요약이 완료되었습니다.",
        data=NoticeData(summary=summary, isCompleted=isCompleted)
    )