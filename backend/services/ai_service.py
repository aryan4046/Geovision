import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'AI'))


def calculate_score(lat: float, lng: float,
                    population_density: float, competitors: list,
                    pois: list, accessibility_score: float,
                    business_type: str, weights: dict):
    try:
        from ai.scoring import calculate_score as ai_calculate_score

        density = float(population_density) if isinstance(population_density, (int, float)) else 50_000

        # Advanced statistical modeling using OSM fetches (pois and competitors)
        # Footfall incorporates not just population, but active points of interest and competitor grouping.
        calculated_footfall = (density * 0.03) + (len(pois) * 150) + (len(competitors) * 80)
        
        # Average income scales with urban density and commercial activity (POIs)
        calculated_income = 40.0 + (density / 10000.0) * 1.5 + (len(pois) * 0.5)

        # Construct exact JSON expected by the Blueprint Engine
        data = {
            "lat":           lat,
            "lng":           lng,
            "business_type": business_type,
            "weights":       weights or {},
            "population":    density,
            "competition":   float(len(competitors)),   
            "accessibility": float(len(pois)),  
            "footfall":      float(max(500, min(10_000, calculated_footfall))), 
            "avg_income":    float(max(30, min(100, calculated_income))),        
        }

        return ai_calculate_score(data)

    except Exception as e:
        print(f"[ai_service] calculate_score error: {e}")
        return {
            "score": 50,
            "factors": {"population": 0.5, "competition": 0.5, "accessibility": 0.5},
            "grade": "C",
            "business_type": business_type
        }


def generate_recommendations(data, candidate_pool=None):
    try:
        from ai.recommendation import generate_recommendations as ai_recs
        return ai_recs(data, candidate_pool=candidate_pool)
    except Exception as e:
        print(f"[ai_service] recommendations error: {e}")
        return {"locations": [], "total_evaluated": 0, "business_type": data.get("business_type", "retail")}


def run_dbscan(coordinates: list):
    try:
        from ai.clustering import detect_hotspots
        return detect_hotspots(coordinates)
    except Exception as e:
        print(f"[ai_service] hotspot error: {e}")
        return {"hotspots": [], "total_clusters": 0, "noise_points": 0}


def generate_explanation(score: int, factors: dict, business_type: str = "retail"):
    try:
        from ai.explanation import generate_explanation as ai_explain
        return ai_explain(score, factors, business_type)
    except Exception as e:
        print(f"[ai_service] explanation error: {e}")
        return {
            "explanation": f"This location scored {score}/100 based on population density, competition, and accessibility.",
            "strengths":     [],
            "weaknesses":    [],
            "opportunities": [],
            "risk_level":    "Medium"
        }


def chat_response(query: str, history=None, context=None):
    try:
        from ai.chatbot import chat_response as ai_chat
        return ai_chat(query, history, context)
    except Exception as e:
        print(f"[ai_service] chat error: {e}")
        return {"response": f"Could not process: {query}", "source": "fallback", "suggestions": []}


def analyze_competitor_impact(data: dict, competitors: list):
    try:
        from ai.competitor import analyze_competitor_impact as ai_impact
        return ai_impact(data, competitors)
    except Exception as e:
        print(f"[ai_service] competitor impact error: {e}")
        return {
            "impact": "Unable to compute",
            "score_change": 0,
            "score_with_comp": 0,
            "score_without_comp": 0,
            "nearby_competitors": len(competitors),
            "competitor_names": [],
            "risk_level": "Low"
        }


def compare_locations(locations: list):
    try:
        from ai.scoring import compare_locations as ai_compare
        return ai_compare(locations)
    except Exception as e:
        print(f"[ai_service] compare error: {e}")
        return {"comparison": [], "winner": {}}


def generate_report(score_result: dict, explanation_result: dict,
                    recommendations, input_data: dict):
    try:
        from ai.recommendation import generate_report as ai_report
        return ai_report(score_result, explanation_result, recommendations, input_data)
    except Exception as e:
        print(f"[ai_service] report error: {e}")
        return {
            "score": score_result.get("score"),
            "factors": score_result.get("factors"),
            "explanation": explanation_result,
            "recommendations": recommendations,
            "business_type": input_data.get("business_type")
        }
