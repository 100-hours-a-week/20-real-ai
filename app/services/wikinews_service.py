import json
import re
import os
from openai import OpenAI
from app.models.llm_client import get_summarize_response
from app.models.prompt_template import wiki_news_prompt, image_prompt
from app.utils.s3_uploader import upload_image_to_s3
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langsmith import traceable
from langsmith.run_helpers import get_current_run_tree
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

@traceable(name="WikiNews Service", inputs={"title": lambda args, kwargs: args[0], "content": lambda args, kwargs: args[1]})
async def generate_wikinews_service(title: str, content: str, presignedUrl: str, request_id: str) -> tuple[str, str, str, str, bool]:
    formatted_docs = f"[title]: {title}\n[content]: {content}"

    # 문서 요약 및 병합
    merged_summary = await summary_from_document(formatted_docs, request_id)

    # 프롬프트 적용
    prompt = wiki_news_prompt.format(context=merged_summary)

    # LLM 호출
    response = await get_summarize_response(prompt, request_id)
    isCompleted = True

    # JSON 파싱
    try:
        response = re.sub(r'(\\n|\\t|\\r|\n|\t|\r)+', '', response).strip()
        response = re.sub(r'(?<=["}])\s[^\w\s\d"\'{}[],.]+(?=\s})', '', response)
        parsed = json.loads(response)

        headline = parsed.get("headline", "")
        summary = parsed.get("summary", "")
        news = parsed.get("news", "")

        # 이미지 생성
        imageUrl = generate_wikinews_image(news)

        # presigned URL에 업로드
        upload_image_to_s3(imageUrl, presignedUrl)

        # 이미지 최종 URL 반환
        imageUrl = presignedUrl.split("?")[0]
    
    except json.JSONDecodeError:
        # JSON 파싱 실패 시 fallback 처리
        isCompleted = False
        headline = "헤드라인 없음"
        summary = "요약 생성 실패"
        news = "뉴스 생성 실패"
        imageUrl = "이미지 생성 실패"
        run = get_current_run_tree()
        if run:
            run.outputs = {
                "파싱실패원본응답": response
            }
    return headline, summary, news, imageUrl, isCompleted


async def summary_from_document(formatted_docs: str, request_id: str) -> str:
    # 문서 객체 생성 및 분할
    document = Document(page_content=formatted_docs)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=20000,
        chunk_overlap=100
    )
    chunks = splitter.split_documents([document])

    # 각 청크 요약 및 병합
    summaries = []
    for chunk in chunks:
       summary_prompt = f"다음 텍스트를 한국어로 각각 3,000자 이내로 요약해 주세요. `<img>` 태그 또는 이미지 URL이 포함된 HTML 요소는 요약에서 제외해주세요: [본문]:{chunk.page_content}"
       summary = await get_summarize_response(summary_prompt, request_id)
       summaries.append(summary)

    return "\n\n".join(summaries)


def generate_wikinews_image(news: str) -> str:
    # 이미지 프롬프트 구성
    prompt = image_prompt.format(news=news)

    # 이미지 생성 요청
    image_response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        n=1
    )

    return image_response.data[0].url