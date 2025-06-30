from functools import lru_cache
from langchain.schema import Document
from app.core.document_loader import load_and_split_markdown_docs

@lru_cache(maxsize=1)
def get_top_recent_docs(k: int = 3) -> list[Document]:
    docs = load_and_split_markdown_docs()
    sorted_docs = sorted(docs, key=lambda d: d.metadata.get("date_int", 0), reverse=True)
    return sorted_docs[:k]