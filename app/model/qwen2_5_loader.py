from vllm import LLM, SamplingParams
from transformers import AutoTokenizer

# 토크나이저 로딩 (프롬프트용 메시지 생성에 사용)
tokenizer = AutoTokenizer.from_pretrained(
    "Qwen/Qwen2.5-7B-Instruct-GPTQ-Int8",
    trust_remote_code=True
)

# Qwen2.5-7B-Instruct 모델 로딩 (vLLM 사용)
llm = LLM(
    model="Qwen/Qwen2.5-7B-Instruct-GPTQ-Int8",
    dtype="auto",
    trust_remote_code=True
)

sampling_params = SamplingParams(
    temperature=0.3,           # 답변 다양성 (우린 정보형 챗봇이라 높을 필요없음)
    top_p=0.9,                 # 핵심 단어 생성 기준
    max_tokens=512,            # 제한 토큰 수
    stop=["</s>", "\n\n"]      # 이 토큰이 생성되면 답변 중단
)