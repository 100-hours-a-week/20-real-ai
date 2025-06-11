from typing import Dict

class WikiNewsBuffer:
    def __init__(self):
        self._store: Dict[str, dict] = {}

    def set(self, request_id: str, data: dict):
        self._store[request_id] = data

    def get(self, request_id: str) -> dict | None:
        return self._store.get(request_id)

    def delete(self, request_id: str):
        if request_id in self._store:
            del self._store[request_id]

news_buffer = WikiNewsBuffer()  # 싱글톤 인스턴스