from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
from services.ai_service import generate_report

router = APIRouter()

class ReportRequest(BaseModel):
    score: int
    explanation: Dict[str, Any]
    recommendations: List[Any]

@router.post("/generate-report")
async def get_report(request: ReportRequest):
    try:
        result = generate_report(request.score, request.explanation, request.recommendations)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
