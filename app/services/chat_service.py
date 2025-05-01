from core.llm_client import get_chat_response

async def generate_chat_response(question: str) -> str:
    return get_chat_response(question)