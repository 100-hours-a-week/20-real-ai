from app.core.date_utils import parse_relative_dates
from app.core.vector_loader import load_vectorstore
from app.models.prompt_template import chatbot_rag_prompt
from app.models.llm_client import get_chat_response
from app.core.chat_history import get_session_history, chat_history_to_string
from langsmith import traceable

# 상위 2개의 문서를 검색하는 retriever 구성
retriever = load_vectorstore().as_retriever(search_kwargs={"k": 2})

# 사용자별 세션 히스토리에 Q/A message 저장 
@traceable(name="Chat Service V2", inputs={"질문": lambda args, kwargs: args[0], "userId": lambda args, kwargs: args[2]})
async def save_chat_history(userId: int, question: str, answer: str):
    history = get_session_history(userId)
    history.add_user_message(question)
    history.add_ai_message(answer)

async def chat_service(question: str, request_id: str, userId: int) -> str:
    # 질문 전처리 (상대 날짜 -> 절대 날짜)
    parsed_question = parse_relative_dates(question)
    
    # 사용자 히스토리 로딩 및 문자열 반환
    history = get_session_history(userId)
    history_str = chat_history_to_string(history)
    
    # RAG
    docs = retriever.get_relevant_documents(parsed_question)
    context = "\n\n".join([doc.page_content for doc in docs])
    
    # 프롬프트 정의 및 LLM 호출
    prompt = chatbot_rag_prompt.format(history=history_str, context=context, question=parsed_question)
    result = await get_chat_response(prompt, docs, request_id)
    
    # 히스토리 저장
    await save_chat_history(userId, parsed_question, result)

    return result