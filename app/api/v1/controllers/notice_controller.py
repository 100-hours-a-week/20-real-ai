from app.services.notice_service import summarize_notice_service
from app.schemas.notice_schema import NoticeRequest, NoticeResponse, NoticeData
import uuid
from langsmith import traceable

@traceable(name="Notice Controller", inputs={"제목": lambda args, kwargs: args[0].title, "본문": lambda args, kwargs: args[0].content})
async def notice_controller(request: NoticeRequest) -> NoticeResponse:
    request_id = str(uuid.uuid4())

    # 공지사항 요약 서비스 호출
    summary, isCompleted = await summarize_notice_service(request.title, request.content, request_id)

    # 표준 응답 스키마로 래핑하여 반환
    return NoticeResponse(
        message="공지사항 요약이 완료되었습니다.",
        data=NoticeData(summary=summary, isCompleted=isCompleted)
    )