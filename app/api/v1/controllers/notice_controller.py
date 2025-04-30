from app.services.notice_service import summarize_notice_service
from app.schemas.notice_schema import NoticeRequest, NoticeResponse

async def summarize_notice(request: NoticeRequest) -> NoticeResponse:
    summary = await summarize_notice_service(request.title, request.content)
    return {
        "message": "공지사항 요약이 완료되었습니다.",
        "data": {
            "summary": summary
        }
    }