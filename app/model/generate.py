from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
from model.qwen2_5_loader import llm

def generate_response(prompt: str) -> str:
    chain = RunnableLambda(lambda x: prompt) | llm | StrOutputParser()
    return chain.invoke({})