from fastapi import APIRouter, HTTPException
from models.request_models import LocationRequest
from services.ai_service import calculate_score, generate_explanation, generate_recommendations
from services.data_service import get_population_density, get_nearby_competitors, get_nearby_pois, get_accessibility_score, get_all_locations

router = APIRouter()

@router.post("/generate-report")
async def get_report(request: LocationRequest):
    try:
        population    = get_population_density(request.lat, request.lng)
        competitors   = get_nearby_competitors(request.lat, request.lng)
        pois          = get_nearby_pois(request.lat, request.lng)
        accessibility = get_accessibility_score(pois)

        score_result = calculate_score(
            request.lat, request.lng,
            population, competitors, pois, accessibility,
            request.business_type, request.weights
        )

        explanation_result = generate_explanation(
            score_result.get("score", 0),
            score_result.get("factors", {}),
            request.business_type
        )

        all_locations = get_all_locations()
        data = {"business_type": request.business_type, "weights": request.weights}
        recommendations = generate_recommendations(data, candidate_pool=all_locations)

        return {
            "score":           score_result.get("score"),
            "grade":           score_result.get("grade"),
            "factors":         score_result.get("factors"),
            "explanation":     explanation_result,
            "recommendations": recommendations,
            "business_type":   request.business_type
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
