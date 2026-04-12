from fastapi import APIRouter, HTTPException
from models.request_models import LocationRequest
from services.data_service import get_population_density, get_nearby_competitors, get_nearby_pois, get_accessibility_score, get_location_name, get_real_state_data
from services.ai_service import calculate_score, generate_explanation

router = APIRouter()

@router.post("/get-score")
async def get_score(request: LocationRequest):
    try:
        population   = get_population_density(request.lat, request.lng)
        competitors  = get_nearby_competitors(request.lat, request.lng, request.business_type)
        pois         = get_nearby_pois(request.lat, request.lng)
        accessibility = get_accessibility_score(pois)

        result = calculate_score(
            request.lat, request.lng,
            population, competitors, pois, accessibility,
            request.business_type, request.weights
        )

        explanation = generate_explanation(
            result.get("score", 0),
            result.get("factors", {}),
            result.get("business_type", request.business_type)
        )

        loc_name = request.location_name if getattr(request, 'location_name', None) else get_location_name(request.lat, request.lng)
        state_census = get_real_state_data(loc_name)

        result["explanation"] = explanation
        result["location_name"] = loc_name
        result["raw_metrics"] = {
            "population": population,
            "competitors": len(competitors),
            "pois": len(pois),
            "competitor_names": [c.get("name", "Store") for c in competitors[:5]],
            "state_census": state_census
        }
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
