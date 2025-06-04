from app.models.qwen3_loader import tokenizer, llm, sampling_params
from dotenv import load_dotenv
from langsmith import traceable

load_dotenv()

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
async def get_chat_response(prompt: str, docs: str, request_id: str) -> str:
    prompt_str = build_prompt(prompt)
    return await llm_generate(prompt_str, request_id)

# 스트리밍 기반 챗봇 응답 함수 
@traceable(name="Chat LLM Stream", inputs={"질문": lambda args, kwargs: args[0]})
def get_chat_response_stream(prompt: str, docs, request_id: str):

    # 1) 실제 호출할 prompt 구성 (history/context는 이미 포함된 prompt 인자로 넘어왔다고 가정)
    prompt_str = build_prompt(prompt)

    # 2) vLLM 스트리밍 제너레이터 객체 가져오기
    agen = llm.generate(prompt_str, sampling_params, request_id=request_id)

    # 3) “순수 텍스트 청크”만 뽑아서 다시 yield하는 async 제너레이터 래퍼
    async def _wrapper():
        last_text = ""
        async for result in agen:
            if result.outputs and result.outputs[0].text:
                text = result.outputs[0].text

                if text.startswith(last_text):
                    # 앞부분이 같으면 안전하게 잘라서 델타만 추출
                    delta = text[len(last_text):]
                else:
                    # 앞부분이 꼬였으면, 일단 전체를 델타로 간주
                    delta = text

                if delta:
                    yield delta
                    last_text = text

    return _wrapper()