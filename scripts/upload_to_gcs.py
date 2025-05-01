from google.cloud import storage
import os

bucket_name = "choon-assistance-ai-bucket"
source_dir = "vector/faiss_index"
destination_prefix = "vector/faiss_index"

client = storage.Client()
bucket = client.bucket(bucket_name)

# 업로드
for filename in os.listdir(source_dir):
    local_path = os.path.join(source_dir, filename)
    blob = bucket.blob(f"{destination_prefix}/{filename}")
    blob.upload_from_filename(local_path)
    print(f"⬆️ 업로드 완료: {blob.name}")