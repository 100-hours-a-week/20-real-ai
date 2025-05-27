import json
import re
from app.models.llm_client import get_summarize_response
from app.models.prompt_template import notice_summary_prompt

async def summarize_notice_service(title: str, content: str, request_id: str) -> str:
    # 공지 요약 프롬프트 구성 (title은 포함하지 않고 content만 사용)
    prompt = notice_summary_prompt.format(docs=content)

    isCompleted = True
    # LLM 응답 호출
    response = await get_summarize_response(prompt, request_id)

    # JSON 파싱
    try:
        response = re.sub(r'(\\n|\\t|\\r|\n|\t|\r)+', '', response).strip()
        parsed = json.loads(response)
        summary = parsed.get("summary", "")
    except json.JSONDecodeError:
        isCompleted = False
        summary = "요약 생성 실패"
    
    return summary, isCompleted