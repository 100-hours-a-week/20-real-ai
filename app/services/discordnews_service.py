import json
from app.core.llm_client import call_qwen
from app.model.prompt_template import discord_news_prompt

def summarize_discord_news_service(title: str | None, content: str) -> tuple[str, str]:
    # 1. 템플릿 적용
    prompt = discord_news_prompt.format(docs=content)

    isCompleted = True
    # 2. LLM 호출
    response = call_qwen(prompt)

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