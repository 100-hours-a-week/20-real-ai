from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
from app.models.embedding_model import get_embedder
from langchain_text_splitters import MarkdownHeaderTextSplitter

import os

# 1. Markdown 문서 로드 (docs/ 폴더 내 .md 파일 대상)
loader = DirectoryLoader(
    path="docs",
    glob="**/*.md",
    loader_cls=TextLoader,
    use_multithreading=True,
)
docs = loader.load()

# 2. Markdown 문서들을 헤더 기준으로 분할
def split_docs_by_markdown_headers(docs: list[Document]) -> list[Document]:
    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
    ]
    splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on,
        strip_headers=False
    )  

    all_splitted = []
    for doc in docs:
        header_splitted = splitter.split_text(doc.page_content)
        # 메타데이터 유지
        for s in header_splitted:
            s.metadata.update(doc.metadata)
        all_splitted.extend(header_splitted)

    return all_splitted

header_splitted_docs = split_docs_by_markdown_headers(docs)

# 3. 문서 분할
splitter = RecursiveCharacterTextSplitter(
    chunk_size=512,
    chunk_overlap=100,
)
chunks = splitter.split_documents(header_splitted_docs)

# 4. 벡터스토어 생성
embedder = get_embedder()
vectorstore = FAISS.from_documents(chunks, embedding=embedder)

# 5. 로컬 저장
INDEX_SAVE_PATH = "vector/faiss_index"
os.makedirs(INDEX_SAVE_PATH, exist_ok=True)
vectorstore.save_local(INDEX_SAVE_PATH)

print(f"✅ 벡터스토어 저장 완료: {INDEX_SAVE_PATH}")
