from fastapi import APIRouter, HTTPException
from models.request_models import CompareRequest
from services.ai_service import calculate_score
from services.data_service import get_population_density, get_nearby_competitors, get_nearby_pois, get_accessibility_score, get_location_name
from ai.explanation import generate_explanation as ai_explain
import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'AI'))

router = APIRouter()

def enrich_location(loc, idx: int, business_type: str = "retail", weights: dict = None):
    population    = get_population_density(loc.lat, loc.lng)
    competitors   = get_nearby_competitors(loc.lat, loc.lng, business_type)
    pois          = get_nearby_pois(loc.lat, loc.lng)
    accessibility = get_accessibility_score(pois)

    result = calculate_score(
        loc.lat, loc.lng,
        population, competitors, pois, accessibility,
        business_type, weights or {}
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

    loc_name = loc.name if getattr(loc, 'name', None) else get_location_name(loc.lat, loc.lng)
    
    from services.data_service import get_real_state_data
    state_census = get_real_state_data(loc_name)

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
        "state_census":  state_census,
    }

@router.post("/compare")
async def get_comparison(request: CompareRequest):
    try:
        loc1 = enrich_location(request.location1, 0, request.business_type, request.weights)
        loc2 = enrich_location(request.location2, 1, request.business_type, request.weights)

        # Sort best first
        comparison = sorted([loc1, loc2], key=lambda x: x["score"], reverse=True)
        winner = comparison[0]["name"]

        from services.ai_service import chat_response
        
        # Build prompt using full metrics
        prompt = (
            f"Act as a Master Urban Planner and Business Strategist. Compare Location A ({loc1['name']}) with Site Score {loc1['score']}/100 "
            f"and Location B ({loc2['name']}) with Site Score {loc2['score']}/100 for a new '{loc1['business_type']}' business. \n\n"
            f"Location A Details: Population Score={loc1['population']}%, Competition Score={loc1['competition']}%, Accessibility={loc1['accessibility']}%. "
            f"Census Density: {loc1['state_census'].get('density_sqkm', 'N/A')} per km2. \n"
            f"Location B Details: Population Score={loc2['population']}%, Competition Score={loc2['competition']}%, Accessibility={loc2['accessibility']}%. "
            f"Census Density: {loc2['state_census'].get('density_sqkm', 'N/A')} per km2. \n\n"
            f"Write a concise, professional, 3-paragraph executive summary comparing the two sites. "
            f"Explicitly mention why {winner} is the primary recommendation based on these specific data points."
        )
        
        llm_result = chat_response(query=prompt)
        recommendation = llm_result.get("response", "")
        
        if len(recommendation) < 50:
            recommendation = (
                f"Based on AI analysis, {winner} scores higher prioritizing better "
                f"urban clustering and verified accessibility. "
                f"This location is our top recommendation for your {comparison[0]['business_type']} infrastructure."
            )
        
        return {
            "comparison":     comparison,
            "winner":         {"name": winner, "score": comparison[0]["score"]},
            "recommendation": recommendation,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
