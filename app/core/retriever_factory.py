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
def create_ensemble_retriever(weights=(0.3, 0.7)):
    bm25 = create_bm25_retriever(header_splitted_docs)
    faiss = create_faiss_retriever(vectorstore)
    return EnsembleRetriever(retrievers=[bm25, faiss], weights=list(weights))