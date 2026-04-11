from fastapi import APIRouter, HTTPException
from models.request_models import CompetitorRequest
from services.ai_service import analyze_competitor_impact, calculate_score
from services.data_service import get_nearby_competitors, get_population_density, get_nearby_pois, get_accessibility_score

router = APIRouter()

@router.post("/competitor-impact")
async def get_competitor_impact(request: CompetitorRequest):
    try:
        population    = get_population_density(request.lat, request.lng)
        competitors   = get_nearby_competitors(request.lat, request.lng)
        pois          = get_nearby_pois(request.lat, request.lng)
        accessibility = get_accessibility_score(pois)

        data = {
            "lat":           request.lat,
            "lng":           request.lng,
            "business_type": "retail",
            "weights":       {},
            "population":    float(population),
            "accessibility": accessibility,
        }

        result = analyze_competitor_impact(data, competitors)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
