import re
from datetime import datetime
from langchain.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import MarkdownHeaderTextSplitter
from langchain.schema import Document

# 날짜 추출 함수
def extract_date_from_markdown(text: str) -> str | None:
    match = re.search(
        r"##\s*Date\s*[:：]?\s*(\d{4})[.\-](\d{2})[.\-](\d{2})",
        text,
        re.IGNORECASE,
    )
    if match:
        try:
            return datetime.strptime("-".join(match.groups()), "%Y-%m-%d").date().isoformat()
        except ValueError:
            return None
    return None

# Markdown 문서들을 헤더 기준으로 분할
def load_and_split_markdown_docs() -> list[Document]:
    loader = DirectoryLoader(
        path="docs",
        glob="**/*.md",
        loader_cls=TextLoader,
        use_multithreading=True,
    )
    docs = loader.load()

    splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[("#", "Header 1")],
        strip_headers=False
    )

    all_splitted = []
    for doc in docs:
        current_date = None
        current_date_int = None
        header_splitted = splitter.split_text(doc.page_content)

        for s in header_splitted:
            maybe_new_date = extract_date_from_markdown(s.page_content)
            if maybe_new_date:
                current_date = maybe_new_date
                try:
                    current_date_int = int(current_date.replace("-", ""))
                except ValueError:
                    current_date_int = 0

            s.metadata.update(doc.metadata)
            s.metadata["date"] = current_date or ""
            s.metadata["date_int"] = current_date_int or 0

        all_splitted.extend(header_splitted)

    return all_splitted