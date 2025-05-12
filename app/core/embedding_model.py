from langchain_community.embeddings import HuggingFaceEmbeddings

# RAG에서 사용할 다국어 임베딩 모델 정의
def get_embedder():
    return HuggingFaceEmbeddings(
        model_name="intfloat/multilingual-e5-base"
    )