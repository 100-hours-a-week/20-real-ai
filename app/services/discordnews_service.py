from app.model.generate import generate_response

async def summarize_discord_news_service(title: str | None, content: str) -> tuple[str, str]:
    # 제목이 없다면 content 일부를 headline에 사용
    if title:
        headline_prompt = f"[헤드라인 생성]\n{title}"
    else:
        headline_prompt = f"[헤드라인 생성]\n{content[:30]}..."

    summary_prompt = f"[요약 생성]\n{content}"

    # 현재는 dummy 응답으로 처리
    headline = await generate_response(headline_prompt)
    summary = await generate_response(summary_prompt)

    return headline, summary