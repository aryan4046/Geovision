from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from services.ai_service import generate_recommendations

router = APIRouter()

class RecommendationRequest(BaseModel):
    business_type: Optional[str] = "retail"
    lat: Optional[float] = None
    lng: Optional[float] = None

@router.post("/get-recommendations")
async def get_recommendations(request: RecommendationRequest = RecommendationRequest()):
    try:
        # Always use the built-in CANDIDATE_LOCATIONS — never depend on locations.json
        data = {
            "business_type": request.business_type or "retail",
            "weights": {}
        }
        result = generate_recommendations(data, candidate_pool=None)  # None → uses CANDIDATE_LOCATIONS
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get-recommendations")
async def get_recommendations_get():
    try:
        data = {"business_type": "retail", "weights": {}}
        result = generate_recommendations(data, candidate_pool=None)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
