from fastapi import APIRouter
from app.api.v1.endpoints import chat_router, notice_router, discordnews_router

api_router = APIRouter(prefix="/api")

# 버전 관리
api_router.include_router(chat_router.router, prefix="/v1")
api_router.include_router(notice_router.router, prefix="/v1")
api_router.include_router(discordnews_router.router, prefix="/v1")