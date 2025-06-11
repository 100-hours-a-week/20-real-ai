from app.services.wikinews_buffer import news_buffer
from app.utils.s3_uploader import upload_image_to_s3

def finalize_wikinews(uuid: str, presigned_url: str) -> dict:
    # 1. 버퍼에서 뉴스 데이터 가져오기
    data = news_buffer.get(uuid)
    if not data:
        return "헤드라인 없음", "요약 없음", "뉴스 없음", "이미지 없음", False

    # 2. presigned URL에 이미지 업로드
    try:
        upload_image_to_s3(data["imageUrl"], presigned_url)
        image_url = presigned_url.split("?")[0]
    except Exception:
        # 업로드 실패 시 fallback
        image_url = "이미지 업로드 실패"
        data["isCompleted"] = False

    # 3. 결과 반환
    return (
        data["headline"],
        data["summary"],
        data["news"],
        image_url,
        data.get("isCompleted", False)
    )