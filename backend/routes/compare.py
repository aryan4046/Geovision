from fastapi import APIRouter, HTTPException
from models.request_models import CompareRequest
from services.ai_service import calculate_score
from services.data_service import get_population_density, get_nearby_competitors, get_nearby_pois, get_accessibility_score, get_location_name
from ai.explanation import generate_explanation as ai_explain
import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'AI'))

router = APIRouter()

def enrich_location(loc, idx: int, business_type: str = "retail"):
    population    = get_population_density(loc.lat, loc.lng)
    competitors   = get_nearby_competitors(loc.lat, loc.lng)
    pois          = get_nearby_pois(loc.lat, loc.lng)
    accessibility = get_accessibility_score(pois)

    result = calculate_score(
        loc.lat, loc.lng,
        population, competitors, pois, accessibility,
        business_type, {}
    )

    score   = result.get("score", 0)
    grade   = result.get("grade", "C")
    factors = result.get("factors", {})

    # Generate quick explanation for pros/cons
    try:
        expl = ai_explain(score, factors, business_type)
        pros  = expl.get("strengths", [])
        cons  = expl.get("weaknesses", [])
    except Exception:
        pros  = []
        cons  = []

    loc_name = get_location_name(loc.lat, loc.lng)

    return {
        "id":            idx,
        "name":          loc_name,
        "lat":           loc.lat,
        "lng":           loc.lng,
        "score":         score,
        "grade":         grade,
        # Convert to 0-100 for frontend progress bars
        "population":    round(factors.get("population",    0) * 100),
        "accessibility": round(factors.get("accessibility", 0) * 100),
        "competition":   round(factors.get("competition",   0) * 100),
        "pois":          round(factors.get("footfall",      0) * 100),
        "pros":          pros,
        "cons":          cons,
        "business_type": business_type,
    }

@router.post("/compare")
async def get_comparison(request: CompareRequest):
    try:
        loc1 = enrich_location(request.location1, 0)
        loc2 = enrich_location(request.location2, 1)

        # Sort best first
        comparison = sorted([loc1, loc2], key=lambda x: x["score"], reverse=True)
        winner = comparison[0]["name"]

        recommendation = (
            f"Based on AI analysis, {winner} scores higher with better "
            f"population density, accessibility, and fewer direct competitors. "
            f"This location is our top recommendation for your {comparison[0]['business_type']} business."
        )

        return {
            "comparison":     comparison,
            "winner":         {"name": winner, "score": comparison[0]["score"]},
            "recommendation": recommendation,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
