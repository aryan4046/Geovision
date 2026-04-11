from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from services.ai_service import generate_explanation

router = APIRouter()

class ExplanationRequest(BaseModel):
    score: int
    factors: Dict[str, Any]

@router.post("/get-explanation")
async def get_explanation(request: ExplanationRequest):
    try:
        result = generate_explanation(request.score, request.factors)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
