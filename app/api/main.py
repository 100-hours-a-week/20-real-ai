from fastapi import APIRouter
from app.api.v1.endpoints import health_router

api_router = APIRouter()

# Health Check 라우터 연결
api_router.include_router(health_router.router, prefix="", tags=["Health Check"])