import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

def calculate_score(population_data, competitor_data, poi_data, business_type, weights):
    try:
        from ai.scoring import calculate_score as ai_calculate_score
        return ai_calculate_score(population_data, competitor_data, poi_data, business_type, weights)
    except ModuleNotFoundError:
        return {"score": 85, "factors": {"population": 30, "competitors": -10, "pois": 65}}

def generate_recommendations():
    try:
        from ai.recommendation import generate_recommendations as ai_generate_recommendations
        return ai_generate_recommendations()
    except ModuleNotFoundError:
        return [{"lat": 0.0, "lng": 0.0, "reason": "Mock recommendation"}]

def run_dbscan():
    try:
        from ai.clustering import run_dbscan as ai_run_dbscan
        return ai_run_dbscan()
    except ModuleNotFoundError:
        return {"clusters": []}

def generate_explanation(score: int, factors: dict):
    try:
        from ai.explanation import generate_explanation as ai_generate_explanation
        return ai_generate_explanation(score, factors)
    except ModuleNotFoundError:
        return {"explanation": "This is a dummy AI explanation."}

def chat_response(query: str):
    try:
        from ai.chatbot import chat_response as ai_chat_response
        return ai_chat_response(query)
    except ModuleNotFoundError:
        return {"response": f"Mock response for query: {query}"}

def analyze_competitor_impact():
    try:
        from ai.competitor import analyze_competitor_impact as ai_analyze_competitor_impact
        return ai_analyze_competitor_impact()
    except ModuleNotFoundError:
        return {"impact": "high", "score_change": -5}

def compare_locations(locations: list):
    try:
        from ai.compare import compare_locations as ai_compare_locations
        return ai_compare_locations(locations)
    except ModuleNotFoundError:
        return {"comparison_data": {}}

def generate_report(score: int, explanation: dict, recommendations: list):
    try:
        from ai.report import generate_report as ai_generate_report
        return ai_generate_report(score, explanation, recommendations)
    except ModuleNotFoundError:
        return {"report": "Structured report content"}
