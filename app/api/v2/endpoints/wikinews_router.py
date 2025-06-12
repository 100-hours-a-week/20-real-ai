from fastapi import APIRouter
from app.schemas.wikinews_schema import WikiNewsRequest, WikiNewsResponse
from app.api.v2.controllers.wikinews_controller import wiki_news_controller

router = APIRouter()

# 위키 뉴스 요약 API 엔드포인트
@router.post("/news", response_model=WikiNewsResponse)
def wiki_news_endpoint(request: WikiNewsRequest):
    # 위키 뉴스 요약 컨트롤러 호출
    return wiki_news_controller(request)