from fastapi import APIRouter
from app.api.v1.endpoints import chat_router as chat_router_v1, notice_router, discordnews_router
from app.api.v2.endpoints import chat_router as chat_router_v2, wikinews_router

# API prefix 설정
api_router = APIRouter()

# 챗봇 API 등록 → /api/v1/chatbots
api_router.include_router(chat_router_v1.router, prefix="/api/v1", tags=["chatbot"])

# 공지 요약 API 등록 → /api/v1/notices/summarization
api_router.include_router(notice_router.router, prefix="/api/v1", tags=["notice"])

# 디스코드 뉴스 요약 API 등록 → /api/v1/news
api_router.include_router(discordnews_router.router, prefix="/api/v1", tags=["discordnews"])

# 챗봇 API 변경 -> /api/v2/chatbots
api_router.include_router(chat_router_v2.router, prefix="/api/v2", tags=["chatbot"])

# 위키 뉴스 API 등록 -> /api/v2/news
api_router.include_router(wikinews_router.router, prefix="/api/v2", tags=["wikinews"])