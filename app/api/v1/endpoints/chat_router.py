from fastapi import APIRouter
from app.schemas.chat_schema import ChatRequest, ChatResponse
from app.api.v1.controllers.chat_controller import chat_response
from typing import Dict, Any

router = APIRouter()

@router.post("/chatbots", response_model=Dict[str, Any])
async def chat_endpoint(request: ChatRequest):
    return await chat_response(request)