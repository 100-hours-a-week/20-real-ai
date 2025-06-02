import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from app.models.llm_client import get_chat_response

# 모델 경로 설정
safeguard_model_name= "kakaocorp/kanana-safeguard-prompt-2.1b"

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

    # 다음 토큰 1개 생성 
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

#  통합 챗봇 응답 함수
async def secure_chat_response(question: str, request_id: str, user_id: str) -> str:
    safety_token = classify_prompt(question)

    if safety_token == "<SAFE>":
        return await get_chat_response(question, request_id, user_id)
    else:
        return "카카오테크 부트캠프 관련 공지사항만 질문해주세요 😃"

