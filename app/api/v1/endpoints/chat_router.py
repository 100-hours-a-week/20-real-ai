from fastapi import APIRouter
from app.schemas.chat_schema import ChatRequest, ChatResponse
from app.api.v1.controllers.chat_controller import chat_controller

router = APIRouter()

@router.post("/chatbots", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    return await chat_controller(request)