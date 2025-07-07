from transformers import AutoTokenizer, AutoModel
import torch

# 모델 이름 및 디바이스 설정
MODEL_NAME = "sentence-transformers/xlm-r-100langs-bert-base-nli-stsb-mean-tokens"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 모델과 토크나이저 로드 함수
def load_guard_model(model_name: str = MODEL_NAME, device: torch.device = device):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)
    model.to(device)
    model.eval()
    return tokenizer, model