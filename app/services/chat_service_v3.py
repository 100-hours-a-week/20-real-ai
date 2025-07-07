from app.core.date_utils import parse_relative_dates
from app.core.chat_history import get_session_history, chat_history_to_string
from app.core.recent_docs_cache import get_top_recent_docs
from app.core.retriever_factory import create_ensemble_retriever
from app.models.prompt_template import chatbot_rag_prompt
from app.models.llm_client import get_chat_response_stream
from langsmith.run_helpers import get_current_run_tree
from langsmith import traceable
from app.core.llm_validatoin import validate_llm_response

# 앙상블 리트리버
retriever = create_ensemble_retriever()

# 사용자별 세션 히스토리에 Q/A message 저장 
async def save_chat_history(userId: int, question: str, answer: str):
    history = get_session_history(userId)
    history.add_user_message(question)
    history.add_ai_message(answer)

@traceable(name="Chat Service V3", inputs={"질문": lambda args, kwargs: args[0]})
async def chat_service_stream(question: str, request_id: str, userId: int):

    # 질문 전처리 (상대 날짜 -> 절대 날짜)
    parsed_question = parse_relative_dates(question)
        
    # 사용자 히스토리 로딩 및 문자열 반환
    history = get_session_history(userId)
    history_str = chat_history_to_string(history)
        
    # 리트리버를 통해 질문에 관련된 문서를 BM25 + FAISS 앙상블 방식으로 검색
    docs = retriever.get_relevant_documents(parsed_question)
    
    if not docs:
        yield "data: 카카오테크 부트캠프 관련 공지사항만 질문해주세요 😃\n\n"
        yield "event: end_of_stream\ndata: \n\n"
        return

    context = "\n\n".join([doc.page_content for doc in docs])

    # "최근" 또는 "최신" 키워드가 원래 질문에 포함되어 있으면 top_docs 추가 
    top_docs = get_top_recent_docs(k=3)
    if "최근" in question or "최신" in question:
        context += "\n\n" + "\n\n".join([doc.page_content for doc in top_docs])

    # 프롬프트 정의 및 LLM 호출
    prompt = chatbot_rag_prompt.format(history=history_str, context=context, question=parsed_question)
    
    # vLLM 스트리밍 API 호출 
    agen = get_chat_response_stream(prompt, request_id)

    answer_collector = []
    async for chunk in agen:
        yield f"data: {chunk}\n\n"
        answer_collector.append(chunk)

    full_answer = "".join(answer_collector)

    is_valid, _ = validate_llm_response(parsed_question, full_answer)

    if not is_valid:
        fallback_msg = "조금 엉뚱한 답변일 수 있어요. 다시 질문해 주시면 더 정확히 도와드릴게요 😊"
        yield f"data: {fallback_msg}\n\n"
        full_answer = fallback_msg

    run = get_current_run_tree()
    if run:
        run.add_outputs({"request_id": request_id,"답변": full_answer})

    # 스트리밍 종료 알림 이벤트
    yield "event: end_of_stream\ndata: \n\n"
    
    # 히스토리 저장
    await save_chat_history(userId, parsed_question, full_answer)
