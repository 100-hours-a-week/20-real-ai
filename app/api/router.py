from fastapi import APIRouter
from app.api.v1.endpoints import chat_router, notice_router, discordnews_router

# API prefix 설정
api_router = APIRouter(prefix="/api/v1")

# 챗봇 API 등록 → /api/v1/chatbots
api_router.include_router(chat_router.router)

# 공지 요약 API 등록 → /api/v1/notices/summarization
api_router.include_router(notice_router.router)

# 디스코드 뉴스 요약 API 등록 → /api/v1/news
api_router.include_router(discordnews_router.router)