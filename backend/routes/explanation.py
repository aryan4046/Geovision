from fastapi import APIRouter, HTTPException
from models.request_models import ExplanationRequest
from services.ai_service import generate_explanation, calculate_score
from services.data_service import get_population_density, get_nearby_competitors, get_nearby_pois, get_accessibility_score

router = APIRouter()

@router.post("/get-explanation")
async def get_explanation(request: ExplanationRequest):
    try:
        population    = get_population_density(request.lat, request.lng)
        competitors   = get_nearby_competitors(request.lat, request.lng)
        pois          = get_nearby_pois(request.lat, request.lng)
        accessibility = get_accessibility_score(pois)

        score_result = calculate_score(
            request.lat, request.lng,
            population, competitors, pois, accessibility,
            request.business_type, {}
        )

        result = generate_explanation(
            score_result.get("score", 0),
            score_result.get("factors", {}),
            request.business_type
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
