from fastapi import APIRouter
from app.schemas.discordnews_schema import DiscordNewsRequest, DiscordNewsResponse
from app.api.v1.controllers.discordnews_controller import summarize_discord_news
from typing import Dict, Any

router = APIRouter()

@router.post("/news", response_model=Dict[str, Any])
async def discord_news_endpoint(request: DiscordNewsRequest):
    return await summarize_discord_news(request)