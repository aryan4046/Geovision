from fastapi import APIRouter, HTTPException
from models.request_models import ChatRequest
from services.ai_service import chat_response

router = APIRouter()

@router.post("/chat")
async def chat(request: ChatRequest):
    try:
        result = chat_response(request.query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
