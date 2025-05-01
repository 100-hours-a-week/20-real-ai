from langchain_community.llms import VLLM

llm = VLLM(
    model="Qwen/Qwen2.5-7B-Instruct",
    trust_remote_code=True,
    max_tokens=512,
    temperature=0.3
)