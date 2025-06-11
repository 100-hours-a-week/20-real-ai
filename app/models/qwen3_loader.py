from vllm import SamplingParams, AsyncEngineArgs, AsyncLLMEngine
from transformers import AutoTokenizer

# 토크나이저 로딩 (프롬프트용 메시지 생성에 사용)
tokenizer = AutoTokenizer.from_pretrained(
    "Qwen/Qwen3-8B-AWQ",
    trust_remote_code=True
)

engine_args = AsyncEngineArgs(
    model="Qwen/Qwen3-8B-AWQ",
    gpu_memory_utilization=0.8,
    tensor_parallel_size=1,
    max_num_seqs=128
)

llm = AsyncLLMEngine.from_engine_args(engine_args)

sampling_params = SamplingParams(
    temperature=0.7,           # 답변 다양성 (우린 정보형 챗봇이라 높을 필요없음)
    top_p=0.8,                 # 핵심 단어 생성 기준
    max_tokens=512,            # 제한 토큰 수
    stop=["</s>", "\n\n"]      # 이 토큰이 생성되면 답변 중단
)