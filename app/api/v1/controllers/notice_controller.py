from app.services.notice_service import summarize_notice_service
from app.schemas.notice_schema import NoticeRequest, NoticeResponse, NoticeData
import uuid

async def summarize_notice(request: NoticeRequest) -> NoticeResponse:
    request_id = str(uuid.uuid4())

    summary, isCompleted = await summarize_notice_service(request.title, request.content, request_id)

    return NoticeResponse(
        message="공지사항 요약이 완료되었습니다.",
        data=NoticeData(summary=summary, isCompleted=isCompleted)
    )