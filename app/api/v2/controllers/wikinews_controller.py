from app.schemas.wikinews_schema import WikiNewsRequest, WikiNewsResponse, WikiNewsData
from app.services.wikinews_service import generate_wikinews_service
import uuid
from langsmith import traceable

@traceable(name="WikiNews Controller", inputs={"제목": lambda args, kwargs: args[0].title, "본문": lambda args, kwargs: args[0].content})
async def wiki_news_controller(request: WikiNewsRequest) -> WikiNewsResponse:
    request_id = str(uuid.uuid4())

    # 헤드라인, 요약, 뉴스, 이미지 서비스 호출
    headline, summary, news, imageUrl, isCompleted = await generate_wikinews_service(request.title, request.content, request.presignedUrl, request_id)

    # 표준 응답 스키마로 래핑하여 반환
    return WikiNewsResponse(
        message="뉴스 생성이 완료되었습니다.",
        data=WikiNewsData(headline=headline, summary=summary, news=news, imageUrl=imageUrl, isCompleted=isCompleted)
    )