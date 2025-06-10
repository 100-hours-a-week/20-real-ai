# 챗봇 히스토리 저장 (인메모리)
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import AIMessage, HumanMessage, BaseMessage
from pydantic import BaseModel, Field
from typing import List

MAX_HISTORY_MESSAGES = 6  # 최대 저장 메시지 수

class InMemoryHistory(BaseChatMessageHistory, BaseModel):
    messages: list[BaseMessage] = Field(default_factory=list)

    def _trim(self):
        """최신 MAX_HISTORY_MESSAGES 개만 유지"""
        if len(self.messages) > MAX_HISTORY_MESSAGES:
            self.messages = self.messages[-MAX_HISTORY_MESSAGES:]

    def add_messages(self, messages: list[BaseMessage]) -> None:
        self.messages.extend(messages)
        self._trim()

    def clear(self) -> None:
        self.messages = []

    def get_messages(self) -> list[BaseMessage]:
        return self.messages

    def add_user_message(self, message: str) -> None:
        self.messages.append(HumanMessage(content=message))
        self._trim()

    def add_ai_message(self, message: str) -> None:
        self.messages.append(AIMessage(content=message))
        self._trim()

# 사용자별 메모리
store = {}
def get_session_history(userId: int) -> BaseChatMessageHistory:
    if (userId) not in store:
        store[(userId)] = InMemoryHistory()
    return store[(userId)]

# 히스토리를 문자열로 반환
def chat_history_to_string(history: InMemoryHistory) -> str:
    messages = history.get_messages()

    lines = []
    for msg in messages:
        role = "사용자" if msg.type == "human" else "AI"
        lines.append(f"{role}: {msg.content}")

    return "\n".join(lines)