from fastapi import APIRouter, HTTPException
from models.request_models import CompareRequest
from services.ai_service import compare_locations

router = APIRouter()

@router.post("/compare")
async def compare(request: CompareRequest):
    try:
        result = compare_locations(request.locations)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
