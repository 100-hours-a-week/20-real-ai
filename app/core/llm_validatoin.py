import torch
from sentence_transformers import util
from app.models.guardrail_model import load_guard_model

# Mean Pooling 
def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[0]
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)


# 출력 검증 함수
def validate_llm_response(prompt: str, response: str, threshold: float = 0.8) -> tuple[bool, float]:
    # 모델, 토크나이저, 디바이스 로드
    tokenizer, model = load_guard_model()

    # 입력 인코딩
    sentences = [prompt, response]
    encoded_input = tokenizer(sentences, padding=True, truncation=True, return_tensors='pt').to(device)

    # 모델 추론
    with torch.no_grad():
        model_output = model(**encoded_input)

    # 평균 풀링 및 정규화
    sentence_embeddings = mean_pooling(model_output, encoded_input['attention_mask'])
    sentence_embeddings = torch.nn.functional.normalize(sentence_embeddings, p=2, dim=1)

    # 코사인 유사도 계산
    similarity_score = util.cos_sim(sentence_embeddings[0], sentence_embeddings[1]).item()
    is_valid = similarity_score >= threshold
    return is_valid, similarity_score

