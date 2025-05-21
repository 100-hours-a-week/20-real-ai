from app.model.qwen2_5_loader import tokenizer, llm, sampling_params
from app.model.prompt_template import chatbot_rag_prompt
from app.core.vector_store import load_vectorstore
from dotenv import load_dotenv
from langsmith import traceable
from langsmith.run_context import tracing_context

load_dotenv()

# 시스템 메시지
SYSTEM_MESSAGE = "You are a kind and friendly chatbot for announcements. Answer politely and clearly based on the announcement content. Please respond only in Korean."

# 벡터스토어 로딩 후 RAG용 retriever 구성
faiss_vectorstore = load_vectorstore()
retriever = faiss_vectorstore.as_retriever()

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
        add_generation_prompt=True
    )

# 비동기 generator(agen)에서 마지막 응답 요소만 수집
async def get_last_output(agen) -> str:
    last_text = ""
    async for item in agen:
        if item.outputs and item.outputs[0].text:
            last_text = item.outputs[0].text
    return last_text

# 공통 LLM 호출 유틸 함수
@traceable(name="LLM 호출")
async def llm_generate(prompt_str: str, request_id: str) -> str:
    agen = llm.generate(prompt_str, sampling_params, request_id=request_id)
    result = await get_last_output(agen)
    return result if result else "empty:" + prompt_str

# 요약/뉴스 생성 전용 호출 함수
async def call_qwen(prompt: str, request_id: str) -> str:
    prompt_str = build_prompt(prompt)
    return await llm_generate(prompt_str, request_id)

# 문서 기반 챗봇 응답 함수
@traceable(name="챗봇 질문 응답", inputs={"질문": lambda args, kwargs: args[0]})
async def get_chat_response(question: str, request_id: str) -> str:
    docs = retriever.get_relevant_documents(question)
    context = "\n\n".join([doc.page_content for doc in docs])
    prompt = chatbot_rag_prompt.format(context=context, question=question)
    prompt_str = build_prompt(prompt)

    get_chat_response.set_outputs({
        "검색된 문서 수": len(docs),
        "첫 문서": docs[0].page_content[:100] if docs else "없음"
    })

    return await llm_generate(prompt_str, request_id)