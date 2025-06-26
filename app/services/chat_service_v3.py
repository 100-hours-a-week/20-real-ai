from app.core.date_utils import parse_relative_dates
from app.core.chat_history import get_session_history, chat_history_to_string
from app.models.prompt_template import chatbot_rag_prompt
from app.models.llm_client import get_chat_response_stream
from langsmith.run_helpers import get_current_run_tree
from langsmith import traceable
from langchain.retrievers import BM25Retriever, EnsembleRetriever
from qdrant_client import models
import arrow
from langchain.schema import Document
from scripts.qdrant.create_vectorstore import client, vectorstore, header_splitted_docs

# 앙상블 리트리버
def create_bm25_retriever(header_splitted_docs):
    # 텍스트 기반 검색기
    bm25_retriever = BM25Retriever.from_documents(
        header_splitted_docs,
        )
    bm25_retriever.k = 1
    return bm25_retriever

def create_qdrant_retriever(vectorstore):  
    # 벡터 기반 검색기
    retriever = vectorstore.as_retriever(
        search_type="similarity_score_threshold",         # 유사도 점수 기반 필터링
        search_kwargs={"k": 2, "score_threshold": 0.7}
    )
    return retriever

def create_ensemble_retriever(retrievers, weights):
    ensemble_retriever = EnsembleRetriever(
        retrievers=retrievers,
        weights=weights
    )
    return ensemble_retriever

# 최종 리트리버 생성
retriever = create_ensemble_retriever(
    [create_bm25_retriever(header_splitted_docs), create_qdrant_retriever(vectorstore)],
    weights=[0.3, 0.7]
    )

# Qdrant 필터링
def get_documents_by_qdrant(client, collection_name: str, tz: str = 'Asia/Seoul'):
    today_int = int(arrow.now(tz).format("YYYYMMDD"))

    search_filter = models.Filter(
        must=[
            models.FieldCondition(
                key="metadata.date_int",
                range=models.Range(lte=today_int)
            )
        ]
    )

    search_result = client.search(
        collection_name=collection_name,
        query_vector=[0.0] * 768,  # dummy vector for non-semantic search
        limit=3,
        with_payload=True,
        with_vectors=False,
        query_filter=search_filter
    )

    # date_int 기준 내림차순 정렬
    sorted_points = sorted(
        search_result,
        key=lambda p: p.payload["metadata"].get("date_int", 0),
        reverse=True
    )

    return sorted_points

# Qdrant record(list)를 LangChain Document로 변환
def qdrant_records_to_documents(records):
    return [
        Document(
            page_content=rec.payload["page_content"],
            metadata=rec.payload.get("metadata", {})
        )
        for rec in records
    ]

# 사용자별 세션 히스토리에 Q/A message 저장 
async def save_chat_history(userId: int, question: str, answer: str):
    history = get_session_history(userId)
    history.add_user_message(question)
    history.add_ai_message(answer)

# 메인 스트리밍 챗 서비스 함수
@traceable(name="Chat Controller V3", inputs={"질문": lambda args, kwargs: args[0]})
async def chat_service_stream(question: str, request_id: str, userId: int):

    # 질문 전처리 (상대 날짜 -> 절대 날짜)
    parsed_question, date_filter = parse_relative_dates(question)

    # 사용자 히스토리 로딩 및 문자열 반환
    history = get_session_history(userId)
    history_str = chat_history_to_string(history)

    docs = retriever.get_relevant_documents(parsed_question)
    context = "\n\n".join([doc.page_content for doc in docs])

    # "최근" "최신" 키워드 포함된 질문이면 → Qdrant에서 최신 문서 3개 조회
    if date_filter.get("mode") == "latest":
        recently_docs = get_documents_by_qdrant(client, "ChoonChat")
        qdrant_docs = qdrant_records_to_documents(recently_docs)
        metadata = "\n\n".join([
        f"제목: {doc.metadata.get('Header 1', '없음')}\n"
        f"날짜: {doc.metadata.get('date', '없음')}\n"
        f"내용: {doc.page_content}"
        for doc in qdrant_docs
    ])

    else:
      metadata = ""

    # 검색 결과가 없다면 스트리밍 종료 및 안내 메시지 출력
    if not docs:
        yield "data: 카카오테크 부트캠프 관련 공지사항만 질문해주세요 😃\n\n"
        yield "event: end_of_stream\ndata: \n\n"
        return

    # 프롬프트 정의 및 LLM 호출
    prompt = chatbot_rag_prompt.format(history=history_str, context=context, metadata=metadata, question=parsed_question)

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