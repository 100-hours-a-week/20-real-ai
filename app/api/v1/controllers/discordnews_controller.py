from app.schemas.discordnews_schema import DiscordNewsRequest, DiscordNewsResponse, DiscordNewsData
from app.services.discordnews_service import summarize_discord_news_service
import uuid

def summarize_discord_news(request: DiscordNewsRequest) -> DiscordNewsResponse:
    request_id = str(uuid.uuid4())

    # 뉴스 요약 서비스 호출
    headline, summary, isCompleted = summarize_discord_news_service(request.title, request.content, request_id)

    # 표준 응답 스키마로 래핑하여 반환
    return DiscordNewsResponse(
        message="뉴스 헤드라인, 요약 생성이 완료되었습니다.",
        data=DiscordNewsData(headline=headline, summary=summary, isCompleted=isCompleted)
    )