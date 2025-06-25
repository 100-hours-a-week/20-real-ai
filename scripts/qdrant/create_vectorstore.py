from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.schema import Document
from app.models.embedding_model import get_embedder
from langchain_text_splitters import MarkdownHeaderTextSplitter
from datetime import datetime
from qdrant_client import QdrantClient
from langchain_qdrant import QdrantVectorStore
from qdrant_client.models import PayloadSchemaType
from dotenv import load_dotenv
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
    headers_to_split_on = [
        ("#", "Header 1")
    ]
    splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on,
        strip_headers=False
    )  

    all_splitted = []

    # 날짜 메타데이터 추출
    for doc in docs:
        current_date = None
        current_date_int = None
        header_splitted = splitter.split_text(doc.page_content)

        for s in header_splitted:
            # 문단 안에서 새로운 날짜를 찾으면 갱신
            maybe_new_date = extract_date_from_markdown(s.page_content)
            if maybe_new_date:
                current_date = maybe_new_date
                try:
                    current_date_int = int(current_date.replace("-", ""))
                except ValueError:
                    current_date_int = 0

            # 항상 최신 current_date 정보를 반영
            s.metadata.update(doc.metadata)
            s.metadata["date"] = current_date or ""
            s.metadata["date_int"] = current_date_int or 0

        all_splitted.extend(header_splitted)

    return all_splitted

header_splitted_docs = split_docs_by_markdown_headers(docs)

load_dotenv()
embedder = get_embedder()

QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")

# Qdrant 클라이언트 초기화
client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY
)

# QdrantVectorStore를 통해 벡터스토어 생성 및 데이터 삽입
vectorstore = QdrantVectorStore.from_documents(
    documents=header_splitted_docs,
    embedding=embedder,
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
    collection_name="ChoonChat",
    force_recreate=True  # 기존 컬렉션을 삭제하고, 새로운 벡터 차원에 맞게 다시 생성
)

# 필드 인덱스 생성
client.create_payload_index(
    collection_name="ChoonChat",                   # 사용할 컬렉션 이름
    field_name="metadata.date_int",                # 인덱스를 생성할 필드 이름
    field_schema=PayloadSchemaType.INTEGER,        # 필드 타입: 정수형
)

print(f"✅ qdrant 벡터스토어 저장 완료:\n {header_splitted_docs}")