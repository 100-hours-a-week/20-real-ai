from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

# 앱에 공통 예외 핸들러 등록 함수
def add_exception_handlers(app: FastAPI):
    
    # HTTPException (ex. raise HTTPException(status_code=404)) 처리
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "message": exc.detail if isinstance(exc.detail, str) else "요청이 잘못되었습니다.",
                "data": None
            }
        )

    # 입력 유효성 검증 실패 (ex. Pydantic 유효성 검사 실패)
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=400,
            content={
                "message": "입력값이 올바르지 않습니다.",
                "data": None
            }
        )

    # 정의되지 않은 일반 예외 처리 (ex. 코드 에러, 서버 에러 등)
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={
                "message": "서버 내부 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
                "data": None
            }
        )