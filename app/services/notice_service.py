from app.model.generate import generate_response

async def summarize_notice_service(title: str, content: str) -> str:
    # LLM 호출은 나중에 진짜로 연결하고, 지금은 echo용
    summary = await generate_response(f"{title}\n\n{content}")
    return summary