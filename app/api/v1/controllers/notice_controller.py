from fastapi import HTTPException
from app.services.notice_service import summarize_notice_service
from app.schemas.notice_schema import NoticeRequest, NoticeResponse, NoticeData
import uuid

async def notice_controller(request: NoticeRequest) -> NoticeResponse:
    request_id = str(uuid.uuid4())

    # 공지사항 요약 서비스 호출
    summary, isCompleted = await summarize_notice_service(request.title, request.content, request_id)

    # JSON 파싱 실패 시 500 예외로 전파 
    if not isCompleted:
        raise HTTPException(
            status_code=500,
            detail="공지사항 요약 생성 중 JSON 파싱 오류가 발생했습니다."
        )

    # 정상 응답일 경우 표준 응답 스키마로 래핑하여 반환
    return NoticeResponse(
        message="공지사항 요약이 완료되었습니다.",
        data=NoticeData(summary=summary, isCompleted=isCompleted)
    )