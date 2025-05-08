from app.core.llm_client import get_chat_response

# 서비스 계층: 컨트롤러에서 호출되는 챗봇 응답 생성 함수
async def generate_chat_response(question: str) -> str:
    return await get_chat_response(question)