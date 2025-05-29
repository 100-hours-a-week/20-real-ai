from app.core.date_utils import parse_relative_dates
from app.core.vector_loader import load_vectorstore
from app.models.prompt_template import chatbot_rag_prompt
from app.models.llm_client import get_chat_response
from langsmith import traceable

retriever = load_vectorstore().as_retriever(search_kwargs={"k": 2})

@traceable(name="Chat Service", inputs={"질문": lambda args, kwargs: args[0], "request_id": lambda args, kwargs: args[1]})
async def chat_service(question: str, request_id: str) -> str:
    parsed_question = parse_relative_dates(question)
    docs = retriever.get_relevant_documents(parsed_question)
    context = "\n\n".join([doc.page_content for doc in docs])
    prompt = chatbot_rag_prompt.format(context=context, question=parsed_question)
    return await get_chat_response(prompt, docs, request_id)