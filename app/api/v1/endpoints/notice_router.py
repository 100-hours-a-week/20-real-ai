from fastapi import APIRouter
from app.schemas.notice_schema import NoticeRequest, NoticeResponse
from app.api.v1.controllers.notice_controller import notice_controller

router = APIRouter()

# 공지사항 요약 API 엔드포인트
@router.post("/notices/summarization", response_model=NoticeResponse)
async def notice_endpoint(request: NoticeRequest):
    # 공지 요약 컨트롤러 호출
    return await notice_controller(request)