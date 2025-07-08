import pytest
import asyncio
import httpx
import time
import os
from dotenv import load_dotenv

# .env 파일에서 환경 변수 불러오기
load_dotenv()

@pytest.mark.asyncio
async def test_chat_stream():
    # 요청에 사용할 데이터 정의 (예: 사용자 ID와 질문)
    payload = {
        "userId": 1234,
        "question": "최근 공지사항 알려줘"
    }

    # 환경 변수에서 API 엔드포인트 URL 불러오기
    url = os.getenv("CHAT_API_URL")

    # 요청 헤더 정의 (JSON 형식으로 전송)
    headers = {
        "Content-Type": "application/json"
    }

    # httpx 비동기 클라이언트로 SSE 요청 수행
    async with httpx.AsyncClient(timeout=60.0) as client:
        # 전체 요청~응답 시간 측정을 위한 시작 시간 기록
        start_time = time.perf_counter()

        # SSE 방식으로 POST 요청 보내고 응답 스트림 처리
        async with client.stream("POST", url, json=payload, headers=headers) as response:
            # 응답 상태 코드 확인
            assert response.status_code == 200
            # Content-Type이 SSE인지 확인
            assert response.headers["content-type"].startswith("text/event-stream")

            full_data = ""  # 전체 스트림 데이터를 누적할 변수
            async for line in response.aiter_lines():
                # 실제 데이터 라인이면 "data: " 접두어 제거하고 저장
                if line.startswith("data: "):
                    chunk = line.removeprefix("data: ").strip()
                    print(chunk, end="", flush=True)
                    full_data += chunk
                # 스트림 종료 이벤트 감지
                elif line.startswith("event: end_of_stream"):
                    break

        # 응답 시간 측정 종료
        elapsed = time.perf_counter() - start_time
        print(f"\n\n🧪 총 응답 시간: {elapsed:.2f}초")

        # 전체 데이터가 비어있지 않아야 함
        assert len(full_data.strip()) > 0