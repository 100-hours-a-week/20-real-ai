import os
from google.cloud import storage
from langchain_community.vectorstores import FAISS
from app.core.embedding_model import embedder

# 환경변수 또는 config.py에서 관리할 수도 있음
GCS_BUCKET = "choon-assistance-ai-bucket"
GCS_PREFIX = "vector/faiss_index"
LOCAL_INDEX_DIR = "/tmp/faiss_index"

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

def load_vectorstore():
    download_faiss_from_gcs()
    return FAISS.load_local(LOCAL_INDEX_DIR, embeddings=embedder)