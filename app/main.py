from fastapi import FastAPI
from app.api.router import api_router
from app.core.error_handler import add_exception_handlers
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# CORS 설정
origins = [
    "http://test.kakaotech.com",
    "https://dev.kakaotech.com",
    "https://www.kakaotech.com",
    "https://kakaotech.com"
]

# CORS 미들웨어 등록
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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