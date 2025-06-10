import json
import re
from app.models.llm_client import get_summarize_response
from app.models.prompt_template import discord_news_prompt
from langsmith import traceable
from langsmith.run_helpers import get_current_run_tree

@traceable(name="DiscordNews Service", inputs={"title": lambda args, kwargs: args[0], "content": lambda args, kwargs: args[1]})
async def summarize_headiline_discordnews_service(title: str | None, content: str, request_id: str) -> tuple[str, str, bool]:
    # 제목 조건문
    if title:
        formatted_docs = f"[title]: {title}\n[content]: {content}"
    else:
        formatted_docs = f"[content]: {content}"
    # 프롬프트 적용
    prompt = discord_news_prompt.format(docs=formatted_docs)

    # LLM 호출
    response = await get_summarize_response(prompt, request_id)
    isCompleted = True

    # JSON 파싱
    try:
        response = re.sub(r'(\\n|\\t|\\r|\n|\t|\r)+', '', response).strip()
        parsed = json.loads(response)
        headline = parsed.get("headline", "")
        summary = parsed.get("summary", "")
    except json.JSONDecodeError:
        # JSON 파싱 실패 시 fallback 처리
        isCompleted = False
        headline = "헤드라인 없음"
        summary = "요약 생성 실패"
        run = get_current_run_tree()
        if run:
            run.outputs = {
                "파싱실패원본응답": response
            }

    return headline, summary, isCompleted