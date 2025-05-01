from model.prompt_template import chat_template
from model.generate import generate_response

def get_chat_response(question: str) -> str:
    prompt = chat_template.format(question=question)
    return generate_response(prompt)