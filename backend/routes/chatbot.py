from fastapi import APIRouter, HTTPException
from models.request_models import ChatRequest
from services.ai_service import chat_response

router = APIRouter()

@router.post("/chat")
async def get_chat_response(request: ChatRequest):
    try:
        # Pass the message to "query" matching the internal function signature
        result = chat_response(query=request.message, history=None, context=request.context)
        
        # chat_response returns {"response": "..."} in fallback, ensure it handles output properly
        if isinstance(result, str):
            result = {"response": result}
        elif isinstance(result, dict) and "response" not in result:
            result = {"response": str(result)}
            
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
