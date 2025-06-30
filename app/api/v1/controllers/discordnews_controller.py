from fastapi import HTTPException
from app.schemas.discordnews_schema import DiscordNewsRequest, DiscordNewsResponse, DiscordNewsData
from app.services.discordnews_service import summarize_headiline_discordnews_service
import uuid

async def discord_news_controller(request: DiscordNewsRequest) -> DiscordNewsResponse:
    request_id = str(uuid.uuid4())

    # 뉴스 요약 서비스 호출
    headline, summary, isCompleted = await summarize_headiline_discordnews_service(request.title, request.content, request_id)

    # JSON 파싱 실패 시 500 예외로 전파 
    if not isCompleted:
        raise HTTPException(
            status_code=500,
            detail="뉴스 헤드라인 및 요약 생성 중 JSON 파싱 오류가 발생했습니다."
        )

    # 표준 응답 스키마로 래핑하여 반환
    return DiscordNewsResponse(
        message="뉴스 헤드라인, 요약 생성이 완료되었습니다.",
        data=DiscordNewsData(headline=headline, summary=summary, isCompleted=isCompleted)
    )