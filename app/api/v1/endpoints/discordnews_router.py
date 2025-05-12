from fastapi import APIRouter
from app.schemas.discordnews_schema import DiscordNewsRequest, DiscordNewsResponse
from app.api.v1.controllers.discordnews_controller import summarize_discord_news

router = APIRouter()

# Discord 뉴스 요약 API 엔드포인트
@router.post("/news", response_model=DiscordNewsResponse)
async def discord_news_endpoint(request: DiscordNewsRequest):
    # 뉴스 요약 컨트롤러 호출
    return await summarize_discord_news(request)