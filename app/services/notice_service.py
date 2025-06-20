import json
import re
from app.models.llm_client import get_summarize_response
from app.models.prompt_template import notice_summary_prompt
from langsmith import traceable
from langsmith.run_helpers import get_current_run_tree

@traceable(name="Notice Service", inputs={"title": lambda args, kwargs: args[0], "content": lambda args, kwargs: args[1]})
async def summarize_notice_service(title: str, content: str, request_id: str) -> tuple[str, bool]:
    formatted_docs = f"[title]: {title}\n[content]: {content}"
    # 프롬프트 적용
    prompt = notice_summary_prompt.format(docs=formatted_docs)

    # LLM 호출
    response = await get_summarize_response(prompt, request_id)
    isCompleted = False

    # JSON 파싱
    try:
        response = re.sub(r'(\\n|\\t|\\r|\n|\t|\r)+', '', response).strip()
        parsed = json.loads(response)
        summary = parsed.get("summary", "")
    except json.JSONDecodeError:
        isCompleted = False
        summary = "요약 생성 실패"
        run = get_current_run_tree()
        if run:
            run.outputs = {
                "파싱실패원본응답": response
            }
    
    return summary, isCompleted