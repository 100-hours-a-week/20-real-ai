from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
from app.models.embedding_model import get_embedder
from langchain_text_splitters import MarkdownHeaderTextSplitter
from datetime import datetime
import re
import os

# 1. Markdown 문서 로드 (docs/ 폴더 내 .md 파일 대상)
loader = DirectoryLoader(
    path="docs",
    glob="**/*.md",
    loader_cls=TextLoader,
    use_multithreading=True,
)
docs = loader.load()

# 2. 날짜 추출 함수
def extract_date_from_markdown(text: str) -> str | None:
    match = re.search(r"^##\s+(\d{4}-\d{2}-\d{2})", text, re.MULTILINE)
    if match:
        try:
            date_obj = datetime.strptime(match.group(1), "%Y-%m-%d").date()
            return date_obj.isoformat()
        except ValueError:
            return None
    return None

# 3. Markdown 문서들을 헤더 기준으로 분할
def split_docs_by_markdown_headers(docs: list[Document]) -> list[Document]:
    headers_to_split_on = [("#", "Header 1")]
    splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on,
        strip_headers=False
    )  

    all_splitted = []
    for doc in docs:
        header_splitted = splitter.split_text(doc.page_content)
        # 메타데이터 
        for s in header_splitted:
            # 문서 블록에서 날짜(예: ## 2025-06-01)를 추출하여 메타데이터로 저장
            date = extract_date_from_markdown(s.page_content)
            s.metadata.update(doc.metadata)
            # "최근" 같은 사용자 질문을 처리할 수 있도록 날짜 정보를 메타데이터에 포함
            s.metadata["date"] = date or "" 
        all_splitted.extend(header_splitted)

    return all_splitted

header_splitted_docs = split_docs_by_markdown_headers(docs)

# 4. 문서 분할
splitter = RecursiveCharacterTextSplitter(
    chunk_size=512,
    chunk_overlap=100,
)
chunks = splitter.split_documents(header_splitted_docs)

# 5. 벡터스토어 생성
embedder = get_embedder()
vectorstore = FAISS.from_documents(chunks, embedding=embedder)

# 6. 로컬 저장
INDEX_SAVE_PATH = "vector/faiss_index"
os.makedirs(INDEX_SAVE_PATH, exist_ok=True)
vectorstore.save_local(INDEX_SAVE_PATH)

print(f"✅ 벡터스토어 저장 완료: {INDEX_SAVE_PATH}")
