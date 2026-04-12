"""
utils.py — GeoVision AI
Utility functions: Haversine distance, normalization, feature extraction.
"""
from __future__ import annotations

import math
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Haversine distance
# ---------------------------------------------------------------------------

def haversine_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    Return the great-circle distance (km) between two coordinates.
    """
    R = 6371.0  # Earth radius in km

    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lam = math.radians(lng2 - lng1)

    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lam / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


# ---------------------------------------------------------------------------
# Normalization
# ---------------------------------------------------------------------------

def normalize(value: float, min_val: float, max_val: float) -> float:
    """
    Min-max normalize a value to [0, 1]. Returns 0.5 on zero-range input.
    """
    if max_val == min_val:
        return 0.5
    return max(0.0, min(1.0, (value - min_val) / (max_val - min_val)))


def normalize_list(values: List[float]) -> List[float]:
    """Normalize an entire list of floats to [0, 1]."""
    if not values:
        return []
    min_v, max_v = min(values), max(values)
    return [normalize(v, min_v, max_v) for v in values]


# ---------------------------------------------------------------------------
# Feature extraction
# ---------------------------------------------------------------------------

def extract_features(location: Dict[str, Any]) -> Dict[str, float]:
    """
    Extract and validate numeric features from a raw location dict.

    Expected keys (all optional, default to sensible mid-range):
        population      — raw count or density index  (0–∞)
        competition     — number of nearby competitors (0–∞)
        accessibility   — transit / road score         (0–10)
        footfall        — estimated daily foot traffic  (0–∞)
        avg_income      — average household income index (0–100)

    Returns normalised float values in [0, 1].
    """
    raw_pop    = float(location.get("population", 50_000))
    raw_comp   = float(location.get("competition", 5))
    raw_access = float(location.get("accessibility", 5.0))
    raw_foot   = float(location.get("footfall", 500))
    raw_income = float(location.get("avg_income", 50.0))

    # Normalise with domain-specific realistic bounds (from Blueprint)
    pop_norm    = normalize(raw_pop,    0, 150_000)  # typical urban clustering bound
    comp_norm   = normalize(raw_comp,   0, 50)       # Max competitors 50 (higher → more competition (inverted later))
    access_norm = normalize(raw_access, 0, 30)       # Max POIs 30
    foot_norm   = normalize(raw_foot,   0, 10_000)
    income_norm = normalize(raw_income, 0, 100)

    return {
        "population":    round(pop_norm, 4),
        "competition":   round(comp_norm, 4),
        "accessibility": round(access_norm, 4),
        "footfall":      round(foot_norm, 4),
        "avg_income":    round(income_norm, 4),
    }


# ---------------------------------------------------------------------------
# Business-type weight presets
# ---------------------------------------------------------------------------

BUSINESS_WEIGHT_PRESETS: Dict[str, Dict[str, float]] = {
    "retail":      {"population": 80, "accessibility": 40, "competition": 70},
    "restaurant":  {"population": 80, "accessibility": 40, "competition": 70},
    "office":      {"population": 0.20, "competition": 0.20, "accessibility": 0.60},
    "warehouse":   {"population": 40, "accessibility": 60, "competition": 80},
    "ev-station":  {"population": 40, "accessibility": 80, "competition": 30},
    "healthcare":  {"population": 0.50, "competition": 0.25, "accessibility": 0.25},
    "education":   {"population": 0.45, "competition": 0.20, "accessibility": 0.35},
    "hospitality": {"population": 0.30, "competition": 0.35, "accessibility": 0.35},
}


def get_weights(business_type: str, custom_weights: Optional[Dict] = None) -> Dict[str, float]:
    """
    Return weight dict. Custom weights override presets; missing keys filled from preset.
    Weights are normalised to sum to 1.
    """
    preset = BUSINESS_WEIGHT_PRESETS.get(
        (business_type or "retail").lower(),
        BUSINESS_WEIGHT_PRESETS["retail"],
    ).copy()

    if custom_weights:
        for k, v in custom_weights.items():
            if k in preset:
                preset[k] = float(v)

    total = sum(preset.values()) or 1.0
    return {k: round(v / total, 4) for k, v in preset.items()}


# ---------------------------------------------------------------------------
# Sample test data (used by tests at module bottom)
# ---------------------------------------------------------------------------

SAMPLE_LOCATION = {
    "lat": 28.6139,
    "lng": 77.2090,
    "population": 120_000,
    "competition": 8,
    "accessibility": 7.5,
    "footfall": 3_500,
    "avg_income": 65,
    "business_type": "retail",
}

SAMPLE_WEIGHTS = {"population": 0.4, "competition": 0.35, "accessibility": 0.25}


# ---------------------------------------------------------------------------
# Quick self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    dist = haversine_distance(28.6139, 77.2090, 19.0760, 72.8777)
    print(f"Distance Delhi→Mumbai: {dist:.1f} km")

    feats = extract_features(SAMPLE_LOCATION)
    print("Extracted features:", feats)

    weights = get_weights("retail", SAMPLE_WEIGHTS)
    print("Resolved weights:", weights)
