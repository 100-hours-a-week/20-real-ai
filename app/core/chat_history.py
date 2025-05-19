from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import AIMessage, HumanMessage, BaseMessage
from pydantic import BaseModel, Field

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

# 사용자별 메모리  (멀티 사용자 기반)
store = {}
def get_session_history(
    user_id: str, conversation_id: str
) -> BaseChatMessageHistory:
    if (user_id, conversation_id) not in store:
        store[(user_id, conversation_id)] = InMemoryHistory()
    return store[(user_id, conversation_id)]


# 히스토리를 문자열로 반환 (vllm.generate 때문에)
def chat_history_to_string(history: InMemoryHistory) -> str:
    lines = []
    for msg in history.get_messages():
        if msg.type == "human":
            lines.append(f"사용자: {msg.content}")
        elif msg.type == "ai":
            lines.append(f"AI: {msg.content}")
    return "\n".join(lines)