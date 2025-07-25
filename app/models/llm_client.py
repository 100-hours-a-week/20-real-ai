from app.models.qwen3_loader import tokenizer, llm, sampling_params
from langsmith import traceable
import re

# 시스템 메시지
SYSTEM_MESSAGE = "You are a kind and friendly chatbot for announcements who responds based on the previous conversation flow. Always answer in Korean."

# 공통 메시지 생성 및 프롬프트 구성 함수
def build_prompt(user_input: str, context: str = "") -> str:
    full_content = f"{context}\n\n{user_input}" if context else user_input

    messages = [
        {"role": "system", "content": SYSTEM_MESSAGE},
        {"role": "user", "content": full_content}
    ]

    return tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
        enable_thinking=False
        )

# 비동기 generator(agen)에서 마지막 응답 요소만 수집
async def get_last_output(agen) -> str:
    last_text = ""
    async for item in agen:
        if item.outputs and item.outputs[0].text:
            last_text = item.outputs[0].text
    return last_text

# 공통 LLM 호출 유틸 함수
async def llm_generate(prompt_str: str, request_id: str) -> str:
    agen = llm.generate(prompt_str, sampling_params, request_id=request_id)
    result = await get_last_output(agen)
    return result if result else "empty:" + prompt_str

# 요약/뉴스 생성 전용 함수
@traceable(name="Summary LLM Response", inputs={"프롬프트": lambda args, kwargs: args[0]})
async def get_summarize_response(prompt: str, request_id: str) -> str:
    prompt_str = build_prompt(prompt)
    return await llm_generate(prompt_str, request_id)

# 문서 기반 챗봇 응답 함수
@traceable(name="Chat LLM Response", inputs={"질문": lambda args, kwargs: args[0]})
async def get_chat_response(prompt: str, request_id: str) -> str:
    prompt_str = build_prompt(prompt)
    return await llm_generate(prompt_str, request_id)

# 스트리밍 기반 챗봇 응답 함수 
@traceable(name="Chat LLM Response V3", inputs={"질문": lambda args, kwargs: args[0]})
def get_chat_response_stream(prompt: str, request_id: str):
    sent_text = ""
    prompt_str = build_prompt(prompt)
    agen = llm.generate(prompt_str, sampling_params, request_id=request_id)

    async def _wrapper():
        nonlocal sent_text
        async for result in agen:
            text = result.outputs[0].text
            new_text = text[len(sent_text):]
            sent_text = text

            for word in re.findall(r'\s+|\S+', new_text):
                yield word

            if result.finished:
                return

    return _wrapper()