from app.services.wikinews_generate import generate_wikinews
from app.schemas.presigned_schema import PresignedRequest, PresignedResponse, PresignedData
import uuid

async def presigned_controller(request: PresignedRequest) -> PresignedResponse:
    request_id = str(uuid.uuid4())

    # 공지사항 요약 서비스 호출
    fileName, contentType, request_id = await generate_wikinews(request.title, request.content, request_id)

    # 표준 응답 스키마로 래핑하여 반환
    return PresignedResponse(
        message="뉴스 생성이 완료되었습니다.",
        data=PresignedData(fileName=fileName, contentType=contentType, uuid=request_id)
    )