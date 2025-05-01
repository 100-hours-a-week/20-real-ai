from langchain_core.prompts import PromptTemplate

chat_template = PromptTemplate.from_template(
    """다음은 사용자의 질문입니다:

{question}

질문에 대해 정확하고 정중하게 답변해주세요."""
)