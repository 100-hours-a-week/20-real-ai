from app.core.date_utils import parse_relative_dates
from app.core.vector_loader import load_vectorstore
from app.core.chat_history import get_session_history, chat_history_to_string
from app.models.prompt_template import chatbot_rag_prompt
from app.models.llm_client import get_chat_response_stream

# 상위 2개의 문서를 검색하는 retriever 구성
retriever = load_vectorstore().as_retriever(
        search_type="similarity_score_threshold",  
        search_kwargs={"score_threshold": 0.7, "k": 2}
    )

# 사용자별 세션 히스토리에 Q/A message 저장 
async def save_chat_history(userId: int, question: str, answer: str):
    history = get_session_history(userId)
    history.add_user_message(question)
    history.add_ai_message(answer)

async def chat_service_stream(question: str, request_id: str, userId: int):
    # 질문 전처리 (상대 날짜 -> 절대 날짜)
    parsed_question = parse_relative_dates(question)
        
    # 사용자 히스토리 로딩 및 문자열 반환
    history = get_session_history(userId)
    history_str = chat_history_to_string(history)
        
     # RAG
    docs = retriever.get_relevant_documents(parsed_question)
    if not docs:
        yield "data: 카카오테크 부트캠프 관련 공지사항만 질문해주세요 😃\n\n"
        yield "event: end_of_stream\ndata: \n\n"
    context = "\n\n".join([doc.page_content for doc in docs])

    # 프롬프트 정의 및 LLM 호출
    prompt = chatbot_rag_prompt.format(history=history_str, context=context, question=parsed_question)
    
    # vLLM 스트리밍 API 호출 
    agen = get_chat_response_stream(prompt, docs, request_id)

    answer_collector = []
    async for chunk in agen:
        yield f"data: {chunk}\n\n"
        answer_collector.append(chunk)

    # 스트리밍 종료 알림 이벤트
    yield "event: end_of_stream\ndata: \n\n"

    full_answer = "".join(answer_collector)
    
    # 히스토리 저장
    await save_chat_history(userId, parsed_question, full_answer)