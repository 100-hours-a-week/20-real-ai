from fastapi import HTTPException
from app.schemas.wikinews_schema import WikiNewsRequest, WikiNewsResponse, WikiNewsData
from app.services.wikinews_service import generate_wikinews_service
import uuid

async def wiki_news_controller(request: WikiNewsRequest) -> WikiNewsResponse:
    request_id = str(uuid.uuid4())

    # 헤드라인, 요약, 뉴스, 이미지 서비스 호출
    headline, summary, news, imageUrl, isCompleted = await generate_wikinews_service(request.title, request.content, request.presignedUrl, request_id)
    
    # JSON 파싱 실패 시 500 예외로 전파 
    if not isCompleted:
        raise HTTPException(
            status_code=500,
            detail="위키뉴스 생성 중 JSON 파싱 오류가 발생했습니다."
        )
    
    # 표준 응답 스키마로 래핑하여 반환
    return WikiNewsResponse(
        message="뉴스 생성이 완료되었습니다.",
        data=WikiNewsData(headline=headline, summary=summary, news=news, imageUrl=imageUrl, isCompleted=isCompleted)
    )