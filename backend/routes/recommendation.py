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
        from database.load_data import fetch_recommendation_cluster, get_population_density, get_location_name
        from services.ai_service import calculate_score
        
        bus_type = request.business_type or "retail"
        if request.lat is None or request.lng is None:
            raise HTTPException(status_code=400, detail="Latitude and Longitude must be provided to get recommendations.")
        
        lat = request.lat
        lng = request.lng
        
        # 1. Fetch live clustered pseudo-locations via one API call
        clusters = fetch_recommendation_cluster(lat, lng, business_type=bus_type)
        
        candidates = []
        for i, cluster in enumerate(clusters):
            c_lat = cluster["lat"]
            c_lng = cluster["lng"]
            
            # Predict scores locally using our mathematically approximated counts
            pop = get_population_density(c_lat, c_lng)
            
            # mock lists of lengths corresponding to counts to reuse calculate_score cleanly safely
            comps_mock = [{"name": "C"} for _ in range(cluster["comp_count"])]
            pois_mock = [{"name": "P"} for _ in range(cluster["poi_count"])]
            
            # Score locally without triggering another OSM hit!
            score_data = calculate_score(
                c_lat, c_lng, pop, comps_mock, pois_mock, 0,
                bus_type, {}
            )
            # Fetch the real geographical name
            real_name_full = get_location_name(c_lat, c_lng)
            
            # It usually returns "Road/Suburb, City". We split this.
            parts = real_name_full.split(',')
            area_name = parts[0].strip()
            city_name = parts[-1].strip() if len(parts) > 1 else parts[0].strip()
            
            # If the API can only find the overarching city name without specific street data, 
            # keep it pure without appending dummy sector strings.
            if area_name == city_name and "Location" in area_name:
                area_name = f"Grid {c_lat:.3f}, {c_lng:.3f}"
            
            import uuid
            candidates.append({
                "id": str(uuid.uuid4())[:8],
                "name": area_name,
                "city": city_name,
                "lat": c_lat,
                "lng": c_lng,
                "score": score_data.get("score", 50),
                "grade": score_data.get("grade", "C"),
                "factors": score_data.get("factors", {}),
            })
            
        # Select best spots and then randomize 5 of them
        import random
        # First filter out very bad scores if we want 'best', or just take top 10 and pick 5 randomly
        candidates.sort(key=lambda x: x["score"], reverse=True)
        top_candidates = candidates[:10]  # Take top 10 best
        
        # Make it random 5
        final_candidates = random.sample(top_candidates, min(5, len(top_candidates)))
        
        return {
            "locations": final_candidates,
            "total_evaluated": len(candidates),
            "business_type": bus_type
        }
    except HTTPException:
        raise
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
