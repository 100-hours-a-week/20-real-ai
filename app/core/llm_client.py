from app.model.qwen2_5_loader import tokenizer, llm, sampling_params
from app.model.prompt_template import chatbot_rag_prompt
from app.core.vector_store import load_vectorstore

# 시스템 메시지
SYSTEM_MESSAGE = "You are Qwen, created by Alibaba Cloud. You are a helpful assistant. Please respond only in Korean."

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

 # 비동기 generator(agen)에서 첫 번째 응답 요소만 받아오는 헬퍼 함수
 # vLLM의 generate()는 async generator를 반환하므로 첫 토큰 배치만 추출할 때 사용
async def get_first_element(agen):
    async for item in agen:
        return item
    return None

# 공통 LLM 호출 유틸 함수
async def llm_generate(prompt_str: str, request_id: str) -> str:
    outputs = llm.generate(prompt_str, sampling_params, request_id=request_id)
    first_element = await get_first_element(outputs)
    if first_element == None:
        return 'empty:' + prompt_str
    else:
        return first_element.outputs[0].text

# 챗봇: 문서 검색 기반 비동기 응답
async def get_chat_response(question: str, request_id:str) -> str:
    docs = retriever.get_relevant_documents(question)
    context = "\n\n".join([doc.page_content for doc in docs])

    # 템플릿: context + question
    prompt = chatbot_rag_prompt.format(context=context, question=question)
    prompt_str = build_prompt(prompt)

    return await llm_generate(prompt_str, request_id)

# 요약/뉴스 생성: 단일 프롬프트 호출
def call_qwen(prompt: str, request_id: str) -> str:
    prompt_str = build_prompt(prompt)

    outputs = llm.generate(prompt_str, sampling_params, request_id=request_id)
    result = ""
    for out in outputs:
        result += out.outputs[0].text

    return result if result else "empty:" + prompt_str