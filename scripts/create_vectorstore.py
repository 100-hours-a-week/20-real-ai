from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from app.models.embedding_model import get_embedder

import os

# 1. Markdown 문서 로드 (docs/ 폴더 내 .md 파일 대상)
loader = DirectoryLoader(
    path="docs",
    glob="**/*.md",
    loader_cls=TextLoader,
    use_multithreading=True,
)
docs = loader.load()

# 2. 문서 분할
splitter = RecursiveCharacterTextSplitter(
    chunk_size=512,
    chunk_overlap=100,
)
chunks = splitter.split_documents(docs)

# 3. 벡터스토어 생성
embedder = get_embedder()
vectorstore = FAISS.from_documents(chunks, embedding=embedder)

# 4. 로컬 저장
INDEX_SAVE_PATH = "vector/faiss_index"
os.makedirs(INDEX_SAVE_PATH, exist_ok=True)
vectorstore.save_local(INDEX_SAVE_PATH)

print(f"✅ 벡터스토어 저장 완료: {INDEX_SAVE_PATH}")