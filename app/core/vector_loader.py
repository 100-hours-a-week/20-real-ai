import os
from google.cloud import storage
from langchain_community.vectorstores import FAISS
from app.core.embedding_model import get_embedder

# Google Cloud Storage 설정
GCS_BUCKET = "choon-assistance-ai-bucket"
GCS_PREFIX = "vector/faiss_index"
LOCAL_INDEX_DIR = "/tmp/faiss_index"

# GCS에서 FAISS 인덱스 파일들 다운로드
def download_faiss_from_gcs():
    client = storage.Client()
    bucket = client.bucket(GCS_BUCKET)
    blobs = bucket.list_blobs(prefix=GCS_PREFIX)

    os.makedirs(LOCAL_INDEX_DIR, exist_ok=True)

    for blob in blobs:
        if blob.name.endswith("/"):  # 디렉토리 무시
            continue
        filename = os.path.basename(blob.name)
        blob.download_to_filename(os.path.join(LOCAL_INDEX_DIR, filename))

# FAISS 벡터스토어 로딩 (GCS에서 받아온 인덱스 기반)
def load_vectorstore():
    download_faiss_from_gcs()
    embedder = get_embedder()
    return FAISS.load_local(
        LOCAL_INDEX_DIR,
        embeddings=embedder,
        allow_dangerous_deserialization=True
    )