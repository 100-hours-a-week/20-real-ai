from app.core.date_utils import parse_relative_dates
from app.core.vector_loader import load_vectorstore
from app.models.prompt_template import chatbot_rag_prompt
from app.models.llm_client import get_chat_response
from app.core.chat_history import get_session_history, chat_history_to_string
from app.services.histrory_service import save_chat_history

retriever = load_vectorstore().as_retriever(search_kwargs={"k": 2})

async def chat_service(question: str, request_id: str, user_id: str) -> str:
    parsed_question = parse_relative_dates(question)
    history = get_session_history(user_id)
    history_str = chat_history_to_string(history)
    docs = retriever.get_relevant_documents(parsed_question)
    context = "\n\n".join([doc.page_content for doc in docs])
    prompt = chatbot_rag_prompt.format(history=history_str, context=context, question=parsed_question)
    result = await get_chat_response(prompt, docs, request_id, user_id)
    await save_chat_history(user_id, parsed_question, result)

    return result