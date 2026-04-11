from fastapi import APIRouter, HTTPException
from services.ai_service import analyze_competitor_impact

router = APIRouter()

@router.post("/competitor-impact")
async def competitor_impact():
    try:
        result = analyze_competitor_impact()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
