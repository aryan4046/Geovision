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

        # Footfall: proportional to density (city centre → high footfall)
        # Range: 500–10000. Linear mapping from density band.
        footfall = max(500, min(10_000, density * 0.05))

        # Avg income: estimated from density tier (dense urban = higher income)
        # Range: 30–90 (index). Higher density cities have higher disposable income.
        if density >= 150_000:
            avg_income = 75.0
        elif density >= 80_000:
            avg_income = 65.0
        elif density >= 40_000:
            avg_income = 55.0
        else:
            avg_income = 40.0

        data = {
            "lat":           lat,
            "lng":           lng,
            "business_type": business_type,
            "weights":       weights or {},
            # Raw values — ai/utils.py normalizes these internally
            "population":    density,
            "competition":   float(len(competitors)),   # count, 0-50 range normalized in utils
            "accessibility": accessibility_score,        # 0-10 scale normalized in utils
            "footfall":      footfall,                   # 500-10000 normalized in utils
            "avg_income":    avg_income,                 # 30-90 normalized in utils
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
