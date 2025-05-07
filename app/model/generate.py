from app.model.qwen2_5_loader import llm, tokenizer

async def generate_response(prompt: str) -> str:
    messages = [
        {"role": "system", "content": "You are Qwen, created by Alibaba Cloud. You are a helpful assistant. Please respond only in Korean."},
        {"role": "user", "content": prompt}
    ]
    prompt_str = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    return await llm.ainvoke(prompt_str)