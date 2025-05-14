import json
from app.core.llm_client import call_qwen
from app.model.prompt_template import discord_news_prompt

async def summarize_discord_news_service(title: str | None, content: str, request_id: str) -> tuple[str, str]:
    # 제목 조건문
    if title:
        formatted_docs = f"[title]: {title}\n[content]: {content}"
    else:
        formatted_docs = f"[content]: {content}"
    # 1. 템플릿 적용
    prompt = discord_news_prompt.format(docs=formatted_docs)

    isCompleted = True
    # 2. LLM 호출
    response = await call_qwen(prompt, request_id)

    # 3. JSON 파싱
    try:
        parsed = json.loads(response)
        headline = parsed.get("headline", "")
        summary = parsed.get("summary", "")
    except json.JSONDecodeError:
        # JSON 파싱 실패 시 fallback 처리
        isCompleted = False
        headline = "헤드라인 없음"
        summary = "요약 생성 실패"

    return headline, summary, isCompleted