from fastapi import FastAPI, Depends
from app.api.router import api_router
from app.core.auth import verify_api_key
from app.core.error_handler import add_exception_handlers

app = FastAPI(dependencies=[Depends(verify_api_key)])

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