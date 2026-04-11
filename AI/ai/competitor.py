"""
competitor.py — GeoVision AI
Competitor Impact Analyzer.
Endpoint: POST /competitor-impact
"""

from __future__ import annotations

from typing import Any

from .utils import haversine_distance, normalize, extract_features, get_weights
from .scoring import calculate_score


# ---------------------------------------------------------------------------
# Default competitor radius
# ---------------------------------------------------------------------------

DEFAULT_RADIUS_KM = 2.0   # look for competitors within 2 km by default


# ---------------------------------------------------------------------------
# Competitor datasets (in production, replaced by real DB / API queries)
# ---------------------------------------------------------------------------

# Sample competitor database — replace/extend with real data
SAMPLE_COMPETITORS: list[dict] = [
    {"name": "CompetitorA", "lat": 28.6150, "lng": 77.2100, "type": "retail",     "size": "large"},
    {"name": "CompetitorB", "lat": 28.6200, "lng": 77.2050, "type": "retail",     "size": "medium"},
    {"name": "CompetitorC", "lat": 19.0780, "lng": 72.8800, "type": "restaurant", "size": "large"},
    {"name": "CompetitorD", "lat": 19.0740, "lng": 72.8760, "type": "restaurant", "size": "small"},
    {"name": "CompetitorE", "lat": 12.9730, "lng": 77.5950, "type": "office",     "size": "large"},
]


# ---------------------------------------------------------------------------
# Helper: filter competitors within radius
# ---------------------------------------------------------------------------

def _nearby_competitors(
    lat: float,
    lng: float,
    radius_km: float,
    competitors: list[dict],
) -> list[dict]:
    return [
        c for c in competitors
        if haversine_distance(lat, lng, c["lat"], c["lng"]) <= radius_km
    ]


# ---------------------------------------------------------------------------
# Helper: competition factor from competitor list
# ---------------------------------------------------------------------------

def _competition_factor(
    nearby: list[dict],
    max_competitors: int = 20,
) -> float:
    """
    0→ no competition (good), 1→ maximum competition (bad).
    Large competitors count double.
    """
    weighted = sum(2.0 if c.get("size") == "large" else 1.0 for c in nearby)
    return min(1.0, weighted / max_competitors)


# ---------------------------------------------------------------------------
# Core function
# ---------------------------------------------------------------------------

def analyze_competitor_impact(
    data: dict[str, Any],
    competitors: list[dict] | None = None,
    radius_km: float = DEFAULT_RADIUS_KM,
) -> dict[str, Any]:
    """
    Compute the score impact of nearby competitors.

    Parameters
    ----------
    data : dict
        Must include: lat, lng, population, accessibility, business_type
        Should include footfall, avg_income if available.
    competitors : list[dict] | None
        List of competitor dicts. Falls back to SAMPLE_COMPETITORS if None.
    radius_km : float
        Search radius for nearby competitors.

    Returns
    -------
    dict
        {
            "impact":             str,
            "score_change":       int,
            "score_with_comp":    int,
            "score_without_comp": int,
            "nearby_competitors": int,
            "competitor_names":   list[str],
            "risk_level":         str   # Low | Moderate | High | Critical
        }
    """
    competitors = competitors or SAMPLE_COMPETITORS
    lat = float(data.get("lat", 0))
    lng = float(data.get("lng", 0))

    nearby = _nearby_competitors(lat, lng, radius_km, competitors)
    comp_count = len(nearby)

    # ── Score WITH competitors ──────────────────────────────────────────────
    comp_factor_with = _competition_factor(nearby)
    payload_with = {**data, "competition": comp_factor_with * 50}   # denorm → 0-50 scale
    score_with = calculate_score(payload_with)["score"]

    # ── Score WITHOUT competitors ───────────────────────────────────────────
    payload_without = {**data, "competition": 0}
    score_without = calculate_score(payload_without)["score"]

    score_change = score_without - score_with   # positive = competitors are hurting the score

    # ── Human-readable impact ───────────────────────────────────────────────
    if score_change <= 2:
        impact      = "Negligible — competitors have minimal impact on this location."
        risk_level  = "Low"
    elif score_change <= 8:
        impact      = f"Moderate — {comp_count} competitor(s) within {radius_km} km reduce the score by {score_change} points."
        risk_level  = "Moderate"
    elif score_change <= 15:
        impact      = f"High — strong competition ({comp_count} rivals) significantly reduces potential score by {score_change} points."
        risk_level  = "High"
    else:
        impact      = f"Critical — {comp_count} dominant competitor(s) drastically reduce market viability (−{score_change} pts)."
        risk_level  = "Critical"

    return {
        "impact":             impact,
        "score_change":       score_change,
        "score_with_comp":    score_with,
        "score_without_comp": score_without,
        "nearby_competitors": comp_count,
        "competitor_names":   [c.get("name", "Unknown") for c in nearby],
        "risk_level":         risk_level,
    }


# ---------------------------------------------------------------------------
# Quick self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import json

    sample_data = {
        "lat":           28.6139,
        "lng":           77.2090,
        "population":    120_000,
        "accessibility":  7.5,
        "footfall":       3_500,
        "avg_income":    65,
        "business_type": "retail",
    }

    result = analyze_competitor_impact(sample_data)
    print(json.dumps(result, indent=2))
