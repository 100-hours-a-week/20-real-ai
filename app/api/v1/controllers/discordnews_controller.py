from app.schemas.discordnews_schema import DiscordNewsRequest, DiscordNewsResponse
from app.services.discordnews_service import summarize_discord_news_service

async def summarize_discord_news(request: DiscordNewsRequest) -> dict:
    headline, summary = await summarize_discord_news_service(request.title, request.content)
    return {
        "message": "뉴스 헤드라인, 요약 생성이 완료되었습니다.",
        "data": {
            "headline": headline,
            "summary": summary
        }
    }