from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import AIMessage, HumanMessage, BaseMessage
from pydantic import BaseModel, Field
from typing import List

class InMemoryHistory(BaseChatMessageHistory, BaseModel):
    messages: list[BaseMessage] = Field(default_factory=list)

    def add_messages(self, messages: list[BaseMessage]) -> None:
        self.messages.extend(messages)

    def clear(self) -> None:
        self.messages = []

    def get_messages(self) -> list[BaseMessage]:
        return self.messages

    def add_user_message(self, message: str) -> None:
        self.messages.append(HumanMessage(content=message))

    def add_ai_message(self, message: str) -> None:
        self.messages.append(AIMessage(content=message))

# 사용자별 메모리  
store = {}
def get_session_history(
    user_id: str
) -> BaseChatMessageHistory:
    if (user_id) not in store:
        store[(user_id)] = InMemoryHistory()
    return store[(user_id)]


# 요약 함수 
def summarize_old_history(messages: List[BaseMessage]) -> str:
    summary = []
    for msg in messages:
        role = "사용자" if msg.type == "human" else "AI"
        content = msg.content.strip().replace("\n", " ")
        summary.append(f"{role}: {content}")
    return "[요약된 과거 대화]\n" + "\n".join(summary[:5])

# 히스토리를 문자열로 반환하되 요약 포함
def chat_history_to_string(history: InMemoryHistory) -> str:
    messages = history.get_messages()
    MAX_RECENT_MESSAGES = 4  # 최근 4개 메시지 

    if len(messages) <= MAX_RECENT_MESSAGES:
        usable = messages
        summary_str = ""
    else:
        usable = messages[-MAX_RECENT_MESSAGES:]
        summary_str = summarize_old_history(messages[:-MAX_RECENT_MESSAGES])

    lines = []
    # 최근 메시지를 상위권에 배치
    for msg in usable:
        role = "사용자" if msg.type == "human" else "AI"
        lines.append(f"{role}: {msg.content}")

    # 요약은 마지막에 배치 (LLM의 주의도를 낮춤)
    if summary_str:
        lines.append(summary_str)

    return "\n".join(lines)