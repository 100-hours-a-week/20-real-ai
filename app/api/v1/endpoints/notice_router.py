from fastapi import APIRouter
from app.schemas.notice_schema import NoticeRequest, NoticeResponse
from app.api.v1.controllers.notice_controller import summarize_notice
from typing import Dict, Any

router = APIRouter()

@router.post("/notices/summarization", response_model=Dict[str, Any])
async def notice_endpoint(request: NoticeRequest):
    return await summarize_notice(request)