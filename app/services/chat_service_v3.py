from app.core.date_utils import parse_relative_dates
from app.core.vector_loader import load_vectorstore
from app.core.chat_history import get_session_history, chat_history_to_string
from app.models.prompt_template import chatbot_rag_prompt
from app.models.llm_client import get_chat_response_stream
from langsmith.run_helpers import get_current_run_tree
from langsmith import traceable
from langchain.retrievers import BM25Retriever, EnsembleRetriever
from scripts.create_vectorstore import header_splitted_docs, vectorstore

# BM25 리트리버 생성 함수
def create_bm25_retriever(header_splitted_docs):
    # 텍스트 기반 검색기
    bm25_retriever = BM25Retriever.from_documents(
        header_splitted_docs,
        )
    bm25_retriever.k = 1
    return bm25_retriever

# FAISS 리트리버 생성 함수
def create_faiss_retriever(vectorstore):  
    # 벡터 기반 검색기
    retriever = vectorstore.as_retriever(
        search_type="similarity_score_threshold",         # 유사도 점수 기반 필터링
        search_kwargs={"k": 2, "score_threshold": 0.7}
    )
    return retriever

# 앙상블 리트리버 생성 함수
def create_ensemble_retriever(retrievers, weights):
    ensemble_retriever = EnsembleRetriever(
        retrievers=retrievers,
        weights=weights
    )
    return ensemble_retriever

# 최종 리트리버 생성
retriever = create_ensemble_retriever(
    [create_bm25_retriever(header_splitted_docs), create_faiss_retriever(vectorstore)],
    weights=[0.3, 0.7]
    )

# 사용자별 세션 히스토리에 Q/A message 저장 
async def save_chat_history(userId: int, question: str, answer: str):
    history = get_session_history(userId)
    history.add_user_message(question)
    history.add_ai_message(answer)

@traceable(name="Chat Controller V3", inputs={"질문": lambda args, kwargs: args[0]})
async def chat_service_stream(question: str, request_id: str, userId: int):

    # 질문 전처리 (상대 날짜 -> 절대 날짜)
    parsed_question, date_filter = parse_relative_dates(question)
        
    # 사용자 히스토리 로딩 및 문자열 반환
    history = get_session_history(userId)
    history_str = chat_history_to_string(history)
        
    # 리트리버를 통해 질문에 관련된 문서를 BM25 + FAISS 앙상블 방식으로 검색
    docs = retriever.get_relevant_documents(parsed_question)
    if not docs:
        yield "data: 카카오테크 부트캠프 관련 공지사항만 질문해주세요 😃\n\n"
        yield "event: end_of_stream\ndata: \n\n"
        return   
    
    # 문서의 날짜 메타데이터 기준으로 최근 문서만 필터링
    if date_filter.get("start_date"):
        docs = [
            doc for doc in docs
            if doc.metadata.get("date") and doc.metadata["date"] >= date_filter["start_date"]
        ]
        if not docs:
            yield "data: 최근 3일 이내의 공지사항은 없습니다 😅\n\n"
            yield "event: end_of_stream\ndata: \n\n"
            return

    context = "\n\n".join([doc.page_content for doc in docs])

    # 프롬프트 정의 및 LLM 호출
    prompt = chatbot_rag_prompt.format(history=history_str, context=context, question=parsed_question)
    
    # vLLM 스트리밍 API 호출 
    agen = get_chat_response_stream(prompt, docs, request_id)

    answer_collector = []
    async for chunk in agen:
        yield f"data: {chunk}\n\n"
        answer_collector.append(chunk)

    full_answer = "".join(answer_collector)

    run = get_current_run_tree()
    if run:
        run.add_outputs({"request_id": request_id,"답변": full_answer})

    # 스트리밍 종료 알림 이벤트
    yield "event: end_of_stream\ndata: \n\n"
    
    # 히스토리 저장
    await save_chat_history(userId, parsed_question, full_answer)