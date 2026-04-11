"""
recommendation.py — GeoVision AI
Recommendation Engine — ranks candidate locations and returns top picks.
Endpoint: POST /get-recommendations
"""

from __future__ import annotations

from typing import Any

from .scoring import calculate_score
from .utils import haversine_distance


# ---------------------------------------------------------------------------
# Default candidate location bank
# (In production: query from PostGIS / GeoJSON dataset)
# ---------------------------------------------------------------------------

CANDIDATE_LOCATIONS: list[dict] = [
    # Delhi / NCR
    {"id": "DEL-001", "name": "Connaught Place",    "city": "Delhi",   "lat": 28.6315, "lng": 77.2167, "population": 180_000, "competition": 12, "accessibility": 9.2, "footfall": 8_000, "avg_income": 75},
    {"id": "DEL-002", "name": "Lajpat Nagar",       "city": "Delhi",   "lat": 28.5631, "lng": 77.2376, "population": 140_000, "competition":  8, "accessibility": 7.8, "footfall": 5_500, "avg_income": 65},
    {"id": "DEL-003", "name": "Dwarka",              "city": "Delhi",   "lat": 28.5921, "lng": 77.0460, "population": 160_000, "competition":  5, "accessibility": 8.5, "footfall": 4_200, "avg_income": 70},
    {"id": "DEL-004", "name": "Saket",               "city": "Delhi",   "lat": 28.5244, "lng": 77.2066, "population": 120_000, "competition": 10, "accessibility": 8.0, "footfall": 6_000, "avg_income": 80},
    # Mumbai
    {"id": "MUM-001", "name": "Bandra West",         "city": "Mumbai",  "lat": 19.0596, "lng": 72.8295, "population": 200_000, "competition": 15, "accessibility": 8.8, "footfall": 9_000, "avg_income": 85},
    {"id": "MUM-002", "name": "Andheri East",        "city": "Mumbai",  "lat": 19.1136, "lng": 72.8697, "population": 220_000, "competition": 18, "accessibility": 9.0, "footfall": 8_500, "avg_income": 72},
    {"id": "MUM-003", "name": "Thane",               "city": "Mumbai",  "lat": 19.2183, "lng": 72.9781, "population": 190_000, "competition":  9, "accessibility": 7.5, "footfall": 6_000, "avg_income": 68},
    # Bengaluru
    {"id": "BLR-001", "name": "Koramangala",         "city": "Bengaluru","lat": 12.9352, "lng": 77.6245, "population": 150_000, "competition": 14, "accessibility": 7.2, "footfall": 7_000, "avg_income": 80},
    {"id": "BLR-002", "name": "Whitefield",          "city": "Bengaluru","lat": 12.9698, "lng": 77.7499, "population": 130_000, "competition":  7, "accessibility": 7.8, "footfall": 5_000, "avg_income": 78},
    {"id": "BLR-003", "name": "Indiranagar",         "city": "Bengaluru","lat": 12.9784, "lng": 77.6408, "population": 140_000, "competition":  9, "accessibility": 8.0, "footfall": 6_500, "avg_income": 82},
    # Hyderabad
    {"id": "HYD-001", "name": "HITEC City",          "city": "Hyderabad","lat": 17.4504, "lng": 78.3808, "population": 160_000, "competition":  8, "accessibility": 8.5, "footfall": 7_000, "avg_income": 78},
    {"id": "HYD-002", "name": "Banjara Hills",       "city": "Hyderabad","lat": 17.4126, "lng": 78.4460, "population": 110_000, "competition": 11, "accessibility": 7.0, "footfall": 5_000, "avg_income": 85},
    # Pune
    {"id": "PUN-001", "name": "Koregaon Park",       "city": "Pune",    "lat": 18.5362, "lng": 73.8951, "population": 100_000, "competition":  6, "accessibility": 7.5, "footfall": 4_500, "avg_income": 80},
    {"id": "PUN-002", "name": "Viman Nagar",         "city": "Pune",    "lat": 18.5679, "lng": 73.9143, "population": 110_000, "competition":  5, "accessibility": 8.0, "footfall": 4_800, "avg_income": 75},
]


# ---------------------------------------------------------------------------
# Core function
# ---------------------------------------------------------------------------

def generate_recommendations(
    data: dict[str, Any],
    top_n: int = 5,
    city_filter: str | None = None,
    exclude_ids: list[str] | None = None,
    min_score: int = 0,
    candidate_pool: list[dict] | None = None,
) -> dict[str, Any]:
    """
    Rank candidate locations and return the top N recommendations.

    Parameters
    ----------
    data : dict
        {
            "business_type": str,
            "weights": {}   # optional custom weights
        }
    top_n        : int  — number of recommendations to return (3-10)
    city_filter  : str  — optionally restrict to a specific city
    exclude_ids  : list — location IDs to exclude
    min_score    : int  — minimum score threshold (0-100)
    candidate_pool : list — override the default candidate bank

    Returns
    -------
    dict
        {
            "locations": [
                {
                    "id":    str,
                    "name":  str,
                    "city":  str,
                    "lat":   float,
                    "lng":   float,
                    "score": int,
                    "grade": str,
                    "factors": {}
                },
                ...
            ],
            "total_evaluated": int,
            "business_type":   str
        }
    """
    top_n        = max(3, min(10, top_n))
    exclude_ids  = set(exclude_ids or [])
    pool         = candidate_pool or CANDIDATE_LOCATIONS
    business_type = data.get("business_type", "retail")
    weights       = data.get("weights")

    scored = []
    for loc in pool:
        # Apply filters
        if loc["id"] in exclude_ids:
            continue
        if city_filter and loc.get("city", "").lower() != city_filter.lower():
            continue

        # Score the location
        payload = {**loc, "business_type": business_type}
        if weights:
            payload["weights"] = weights

        result = calculate_score(payload)
        if result["score"] < min_score:
            continue

        scored.append(
            {
                "id":      loc["id"],
                "name":    loc["name"],
                "city":    loc.get("city", ""),
                "lat":     loc["lat"],
                "lng":     loc["lng"],
                "score":   result["score"],
                "grade":   result["grade"],
                "factors": result["factors"],
            }
        )

    # Rank by score descending
    scored.sort(key=lambda x: x["score"], reverse=True)

    return {
        "locations":       scored[:top_n],
        "total_evaluated": len(scored),
        "business_type":   business_type,
    }


# ---------------------------------------------------------------------------
# Report Generation helper (used by /report endpoint)
# ---------------------------------------------------------------------------

def generate_report(
    score_result:       dict[str, Any],
    explanation_result: dict[str, Any],
    recommendations:    dict[str, Any],
    input_data:         dict[str, Any],
) -> dict[str, Any]:
    """
    Combine score, explanation, and recommendations into a structured report.

    Returns
    -------
    dict
        Full structured report JSON — ready for PDF or frontend rendering.
    """
    return {
        "report_version": "1.0",
        "generated_at":   _now_iso(),
        "input": {
            "lat":           input_data.get("lat"),
            "lng":           input_data.get("lng"),
            "business_type": input_data.get("business_type", "retail"),
        },
        "site_readiness": {
            "score":   score_result.get("score"),
            "grade":   score_result.get("grade"),
            "factors": score_result.get("factors", {}),
        },
        "ai_explanation": explanation_result,
        "top_recommendations": recommendations.get("locations", [])[:3],
        "summary": (
            f"Site Readiness Score: {score_result.get('score')}/100 | "
            f"Grade: {score_result.get('grade')} | "
            f"Risk: {explanation_result.get('risk_level', 'N/A')}"
        ),
    }


def _now_iso() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Quick self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import json

    result = generate_recommendations(
        data={"business_type": "restaurant"},
        top_n=5,
    )
    print(f"Evaluated: {result['total_evaluated']} | Top {len(result['locations'])} returned")
    for loc in result["locations"]:
        print(f"  [{loc['grade']}] {loc['name']}, {loc['city']} — Score: {loc['score']}")
