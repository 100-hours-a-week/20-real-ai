from fastapi import APIRouter
from app.schemas.chat_schema import ChatRequest, ChatResponse
from app.api.v1.controllers.chat_controller import chat_response

router = APIRouter()

@router.post("/chatbots", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    return chat_response(request)