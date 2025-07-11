import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.monitoring import record_api_request


class MetricsMiddleware(BaseHTTPMiddleware):
    """
    API 요청 메트릭을 자동으로 수집하는 미들웨어
    """
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # 요청 처리
        response = await call_next(request)
        
        # 응답 시간 계산
        duration_ms = (time.time() - start_time) * 1000
        
        # 메트릭 기록
        record_api_request(
            endpoint=str(request.url.path),
            method=request.method,
            status_code=response.status_code,
            duration_ms=duration_ms
        )
        
        return response 