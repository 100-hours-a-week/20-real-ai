from langchain_community.llms import VLLM
from transformers import AutoTokenizer

# 토크나이저 로딩 (프롬프트용 메시지 생성에 사용)
tokenizer = AutoTokenizer.from_pretrained(
    "Qwen/Qwen2.5-7B-Instruct",
    trust_remote_code=True
)

# Qwen2.5-7B-Instruct 모델 로딩 (vLLM 사용)
llm = VLLM(
    model="Qwen/Qwen2.5-7B-Instruct",
    trust_remote_code=True,
    max_tokens=512,
    temperature=0.3
)