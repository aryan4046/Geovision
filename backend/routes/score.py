from fastapi import APIRouter, HTTPException
from models.request_models import LocationRequest
from models.response_models import ScoreResponse
from services.data_service import get_population_density, get_nearby_competitors, get_nearby_pois
from services.ai_service import calculate_score

router = APIRouter()

@router.post("/get-score")
async def get_score(request: LocationRequest):
    try:
        # Load data from database
        # Extract population, competitors, POIs
        population = get_population_density(request.lat, request.lng)
        competitors = get_nearby_competitors(request.lat, request.lng)
        pois = get_nearby_pois(request.lat, request.lng)
        
        # Call calculate_score
        result = calculate_score(population, competitors, pois, request.business_type, request.weights)
        
        # Return {"score": int, "factors": {}}
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
