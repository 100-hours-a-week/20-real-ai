import requests
from langsmith.run_helpers import get_current_run_tree

def download_image_as_bytes(url: str) -> bytes:
    # 이미지 URL에서 바이너리 데이터 다운로드
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    raise Exception(f"[이미지 다운로드 실패] status={response.status_code}, url={url}")


def upload_image_to_s3(image_url: str, presigned_url: str):
    # 이미지를 바이너리로 변환
    image_bytes = download_image_as_bytes(image_url)

    # S3 presigned URL에 PUT 요청으로 업로드
    headers = {
        'Content-Type': 'image/png'
    }
    response = requests.put(presigned_url, data=image_bytes, headers=headers)
    
    run = get_current_run_tree()
    if response.status_code == 200:
        run.add_event("upload_success")
    else:
        run.add_event("upload_failure")
        run.add_outputs({"파싱실패원본응답": response.text})
        # raise Exception(f"❌ 업로드 실패: {response.status_code} - {response.text}")