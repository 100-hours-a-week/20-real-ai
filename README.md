# 💛 춘이네 비서실 🤎 – KakaoTech BootCamp 전용 AI 비서 서비스

카카오테크부트캠프 공지사항을 **더 빠르게, 더 쉽게** 확인하고  
질의응답, 요약, 뉴스 생성까지 가능한 **RAG + 로컬 LLM 기반 AI 비서 시스템**입니다.

<img src="https://media.discordapp.net/attachments/1384817448846491719/1393110511574450278/2025-07-11_15.03.40.png?ex=6871fac4&is=6870a944&hm=d844e982ccf4c98972c6386677af7a40da98a2412d43f8b6dbc8e6fcb97680b8&=&format=webp&quality=lossless&width=688&height=1604" width="45%"/> <img src="https://cdn.discordapp.com/attachments/1384817448846491719/1393111304067219566/2025-07-11_15.06.50.png?ex=6871fb81&is=6870aa01&hm=f99394ad3019389b8b5be694783fc93921e1551e219763272c7575b44c9dbb25&" width="45%"/>

<br>

## 📌 주요 기능

### 🤖 1. 공지사항 기반 챗봇
- 부트캠프 공지에 대한 질의응답 지원
- FAISS + BM25 앙상블 기반 문서 검색
- **vLLM 기반 로컬 LLM 서빙**
- 단어 단위 실시간 **스트리밍 응답 (SSE)**
- 날짜 인식 및 대화 히스토리 처리

### 📰 2. 위키 기반 뉴스 생성
- 위키 문서를 입력으로 받아 뉴스 생성
- **흥미로운 헤드라인**, **핵심 정보 요약**, **친근한 문장 구성**, **적절한 이미지**로 구성
- 이미지 생성 모델과 연동하여 **정보 전달력과 몰입도**를 향상

### 📝 3. 공지사항 요약
- 긴 공지 내용을 한눈에 이해할 수 있도록 요약
- 내부적으로 Qwen3 기반 프롬프트 응답 활용

<br>

## ⚙️ 기술 개요

| 구성 요소 | 설명 |
|-----------|------|
| LLM 엔진 | vLLM + Qwen3 (로컬 실행) |
| 검색 시스템 | FAISS 벡터 검색 + BM25 텍스트 검색 앙상블 |
| 응답 전송 | SSE (Server-Sent Events) 기반 StreamingResponse |
| API 서버 | FastAPI (Python 3.10) |
| 문서 소스 | Markdown (.md) 공지 파일 |
| 세션 관리 | 사용자 ID별 대화 히스토리 저장 |
| 디버깅 도구 | LangSmith 트레이싱 지원 |

<br>

## 🛠️ 실행 환경 및 초기 세팅

### 💻 1. GCP 서버 접속 (VSCode Remote SSH)
```bash
# gcp-key.json 혹은 SSH 키 기반으로 접속
```

### 🧪 2. 가상환경 생성 및 패키지  설치
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 📦 3. 프로젝트 클론
```bash
git clone https://github.com/100-hours-a-week/20-real-ai.git
cd 20-real-ai
```

### ⚙️ 4. 환경변수 파일 생성 (`.env`)
`.env` 파일에는 다음과 같은 항목들이 필요합니다:
```env
# 🔐 AI 서버 인증 (FastAPI Static API Key)
API_KEY=your-api-key

# 🧪 LangSmith 트레이싱 설정
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=your-langsmith-api-key
LANGSMITH_PROJECT=your-langsmith-project-name

# 🤖 OpenAI API Key (이미지 생성 등 외부 연동 시)
OPENAI_API_KEY=your-openai-api-key

# 🌐 내부 챗봇 API 엔드포인트 (테스트 및 백엔드 연동 시 사용)
CHAT_API_URL=http://localhost:8000/api/v3/chatbots
```
env 파일은 FastAPI 서버 실행 전 반드시 루트 디렉토리에 위치해야 하며,
인증, LangSmith 추적, 외부 API 연동 등에 사용됩니다.

### 🚀 5. FastAPI 서버 실행
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### ✅ 테스트 실행
```bash
pytest tests/test_chat_api.py -s
```

### 📁 디렉토리 구조
```
20-real-ai/
├── app/
│   ├── api/               # API 라우터 정의
│   ├── core/              # 인증, 유틸, 예외 처리
│   ├── models/            # LLM 로딩 및 프롬프트
│   ├── services/          # 챗봇, 요약, 뉴스 생성 로직
│   ├── utils/             # 이미지 처리 및 S3 업로드 유틸리티
│   └── main.py            # FastAPI 진입점
├── docs/                  # 공지 .md 문서 (RAG 소스)
├── scripts/               # 벡터스토어 생성 등 유틸 스크립트
├── tests/                 # 테스트 코드
├── requirements.txt
├── .env
└── README.md
```

<br>

## 📚 프로젝트 위키

> 본 프로젝트의 전체 설계 구조, 개발 과정, 기능 흐름 등이 담긴 기술 문서는 아래 위키에서 확인할 수 있습니다.

📎 [춘이네 비서실 위키 바로가기](https://your-wiki-url.com/chunibot)

위키에는 다음 항목들이 정리되어 있습니다:
- 전체 개발 일정과 아키텍처 모듈 구성
- API 명세 및 예시 요청/응답
- 기능별 처리 로직 및 내부 호출 구조
- 모델 서빙, 스트리밍 및 최적화 설계
- LangSmith 기반 디버깅 및 트레이싱 전략