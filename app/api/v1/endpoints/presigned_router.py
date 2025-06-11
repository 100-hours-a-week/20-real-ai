from fastapi import APIRouter
from app.schemas.presigned_schema import PresignedRequest, PresignedResponse
from app.api.v1.controllers.presigned_controller import presigned_controller

router = APIRouter()

# 공지사항 요약 API 엔드포인트
@router.post("/presigned", response_model=PresignedResponse)
async def presigned_endpoint(request: PresignedRequest):
    # 공지 요약 컨트롤러 호출
    return await presigned_controller(request)