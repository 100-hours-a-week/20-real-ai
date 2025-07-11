import os
from fastapi import FastAPI, Depends
from app.api.router import api_router
from app.core.auth import verify_api_key
from app.core.error_handler import add_exception_handlers
from app.core.monitoring import setup_signoz_monitoring, record_system_metrics
from app.core.metrics_middleware import MetricsMiddleware

app = FastAPI(dependencies=[Depends(verify_api_key)])

# SignOz 모니터링 설정
setup_signoz_monitoring(app)
# 시스템 메트릭 기록 활성화
record_system_metrics()

# 메트릭 미들웨어 추가
app.add_middleware(MetricsMiddleware)

# 전체 API 라우터 등록
app.include_router(api_router)

# 예외 핸들러 등록
add_exception_handlers(app)

# 루트 엔드포인트 추가
@app.get("/")
def read_root():
    return {"message": "Hello, this is the 20-real-ai server. API is running."}

# 헬스 체크 엔드포인트
@app.get("/health")
def health_check():
    return {"status": "ok"}