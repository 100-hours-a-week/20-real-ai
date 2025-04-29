from app.model.generate import generate_response

async def generate_chat_response(question: str) -> str:
    # LLM 호출은 나중에 진짜로 연결하고, 지금은 echo용
    answer = await generate_response(question)
    return answer