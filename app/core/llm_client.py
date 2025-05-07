from app.model.qwen2_5_loader import llm, tokenizer
from app.model.prompt_template import chat_prompt_template
from app.core.vector_store import load_vectorstore

faiss_vectorstore = load_vectorstore()
retriever = faiss_vectorstore.as_retriever()

async def get_chat_response(question: str) -> str:
    docs = retriever.get_relevant_documents(question)
    context = "\n\n".join([doc.page_content for doc in docs])
    prompt = chat_prompt_template.format(context=context, question=question)

    messages = [
        {"role": "system", "content": "You are Qwen, created by Alibaba Cloud. You are a helpful assistant. Please respond only in Korean."},
        {"role": "user", "content": prompt}
    ]
    prompt_str = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    return await llm.ainvoke(prompt_str)
