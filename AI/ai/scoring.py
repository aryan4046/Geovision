"""
scoring.py — GeoVision AI
Site Readiness Score + Personalized Scoring Engine.
Endpoint: POST /get-score
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .utils import extract_features, get_weights, normalize


# ---------------------------------------------------------------------------
# Core scoring logic
# ---------------------------------------------------------------------------

def calculate_score(data: dict[str, Any]) -> dict[str, Any]:
    """
    Calculate the Site Readiness Score for a given location.

    Parameters
    ----------
    data : dict
        {
            "lat": float,
            "lng": float,
            "business_type": str,
            "population": float,
            "competition": float,
            "accessibility": float,
            "weights": {                    # optional overrides
                "population": float,
                "competition": float,
                "accessibility": float
            }
        }

    Returns
    -------
    dict
        {
            "score": int,          # 0-100
            "factors": {
                "population":    float,   # normalized 0-1
                "competition":   float,   # normalized 0-1 (inverted)
                "accessibility": float,   # normalized 0-1
                "footfall":      float,
                "avg_income":    float
            },
            "grade":   str,        # A / B / C / D / F
            "business_type": str
        }
    """
    features = extract_features(data)
    weights  = get_weights(data.get("business_type", "retail"), data.get("weights"))

    # Invert competition score: more competitors → lower sub-score
    competition_score = 1.0 - features["competition"]

    # Weighted sum of the three primary factors
    raw_score = (
        features["population"]    * weights["population"]
        + competition_score       * weights["competition"]
        + features["accessibility"] * weights["accessibility"]
    )

    # Bonus boost from footfall and avg_income (small weight, max +10 pts)
    secondary_boost = (features["footfall"] + features["avg_income"]) * 5  # each up to 5 pts

    final_score = min(100, round(raw_score * 100 + secondary_boost))

    factors = {
        "population":    features["population"],
        "competition":   round(competition_score, 4),
        "accessibility": features["accessibility"],
        "footfall":      features["footfall"],
        "avg_income":    features["avg_income"],
    }

    return {
        "score":         final_score,
        "factors":       factors,
        "grade":         _grade(final_score),
        "business_type": data.get("business_type", "retail"),
    }


def _grade(score: int) -> str:
    if score >= 85:
        return "A"
    if score >= 70:
        return "B"
    if score >= 55:
        return "C"
    if score >= 40:
        return "D"
    return "F"


# ---------------------------------------------------------------------------
# Personalized Scoring Engine — compare score across different business types
# ---------------------------------------------------------------------------

def personalized_score(data: dict[str, Any]) -> dict[str, Any]:
    """
    Run calculate_score for every business type and return a ranked table.

    Parameters
    ----------
    data : dict  — base location data (without weights/business_type keys)

    Returns
    -------
    dict
        {
            "best_fit": str,
            "rankings": [
                {"business_type": str, "score": int, "grade": str}, ...
            ]
        }
    """
    from .utils import BUSINESS_WEIGHT_PRESETS

    results = []
    for btype in BUSINESS_WEIGHT_PRESETS:
        payload = {**data, "business_type": btype}
        r = calculate_score(payload)
        results.append({"business_type": btype, "score": r["score"], "grade": r["grade"]})

    results.sort(key=lambda x: x["score"], reverse=True)
    return {
        "best_fit": results[0]["business_type"] if results else "retail",
        "rankings": results,
    }


# ---------------------------------------------------------------------------
# Location Comparison (also served from this module)
# Endpoint: POST /compare
# ---------------------------------------------------------------------------

def compare_locations(locations: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Score multiple locations and return a side-by-side comparison.

    Parameters
    ----------
    locations : list[dict]
        Each element is a full location data dict as expected by calculate_score.

    Returns
    -------
    dict
        {
            "comparison": [
                {
                    "id":      int,
                    "lat":     float,
                    "lng":     float,
                    "score":   int,
                    "grade":   str,
                    "factors": {},
                    "business_type": str
                },
                ...
            ],
            "winner": {"id": int, "score": int}
        }
    """
    comparison = []
    for idx, loc in enumerate(locations):
        result = calculate_score(loc)
        comparison.append(
            {
                "id":            idx,
                "lat":           loc.get("lat"),
                "lng":           loc.get("lng"),
                "score":         result["score"],
                "grade":         result["grade"],
                "factors":       result["factors"],
                "business_type": result["business_type"],
            }
        )

    comparison.sort(key=lambda x: x["score"], reverse=True)
    winner = {"id": comparison[0]["id"], "score": comparison[0]["score"]} if comparison else {}

    return {"comparison": comparison, "winner": winner}


# ---------------------------------------------------------------------------
# Quick self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    from utils import SAMPLE_LOCATION, SAMPLE_WEIGHTS  # noqa: F401 (direct run)

    sample = {**SAMPLE_LOCATION, "weights": SAMPLE_WEIGHTS}
    result = calculate_score(sample)
    print("Score result:", result)

    personal = personalized_score(SAMPLE_LOCATION)
    print("Personalized rankings:", personal)

    comparison = compare_locations([
        {**SAMPLE_LOCATION},
        {**SAMPLE_LOCATION, "lat": 19.076, "lng": 72.877, "population": 200_000, "competition": 15},
    ])
    print("Comparison:", comparison)
