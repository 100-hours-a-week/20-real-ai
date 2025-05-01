from langchain_community.llms import VLLM

# GCP VM에 올라간 Qwen2.5-7B-Instruct 모델을 vLLM으로 감싸 LangChain에서 사용할 수 있게 구성
llm = VLLM(
    model="Qwen/Qwen2.5-7B-Instruct",  # Hugging Face 또는 로컬 경로 가능 (GCP VM에 위치)
    trust_remote_code=True,
    max_tokens=512,
    temperature=0.3
)