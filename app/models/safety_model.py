import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# 모델 경로 설정
safeguard_model_name= "kyuhongtheory/kanana-safeguard-prompt-2.1b-bnb-4bit"

# 모델 및 토크나이저 로드
safeguard_model = AutoModelForCausalLM.from_pretrained(
    safeguard_model_name,
    torch_dtype=torch.float16,
    device_map="auto"
).eval()

safeguard_tokenizer = AutoTokenizer.from_pretrained(safeguard_model_name)

# SAFE/UNSAFE 판별 함수
def classify_prompt(user_prompt: str) -> str:
    messages = [{"role": "user", "content": user_prompt}]

    # 채팅 템플릿 적용 후 토큰화
    input_ids = safeguard_tokenizer.apply_chat_template(messages, tokenize=True, return_tensors="pt").to(safeguard_model.device)
    attention_mask = (input_ids != safeguard_tokenizer.pad_token_id).long()

    # 다음 토큰 1개 생성 (추론)
    with torch.no_grad():
        output_ids = safeguard_model.generate(
            input_ids,
            attention_mask=attention_mask,
            max_new_tokens=1,
            pad_token_id=safeguard_tokenizer.eos_token_id
        )

    # 새로 생성된 토큰만 추출해 디코딩
    gen_idx = input_ids.shape[-1]
    return safeguard_tokenizer.decode(output_ids[0][gen_idx], skip_special_tokens=True).strip() # strip()