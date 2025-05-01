from langchain_core.output_parsers import StrOutputParser
from app.model.qwen2_5_loader import llm
from app.model.prompt_template import chat_prompt
from app.core.vector_store import load_vectorstore

# ✅ FAISS 기반 retriever 로드
faiss_vectorstore = load_vectorstore()
retriever = faiss_vectorstore.as_retriever()

# ✅ 사용자 질문 → RAG 기반 응답 생성
def get_chat_response(question: str) -> str:
    # 유사 문서 검색
    docs = retriever.get_relevant_documents(question)

    # context 조합 (텍스트만 추출)
    context = "\n\n".join([doc.page_content for doc in docs])

    # LangChain 체인 구성
    chain = chat_prompt | llm | StrOutputParser()

    # 실행
    return chain.invoke({
        "context": context,
        "question": question
    })