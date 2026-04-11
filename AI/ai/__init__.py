"""
GeoVision AI module — public API surface.
"""

from .scoring       import calculate_score, personalized_score, compare_locations
from .clustering    import detect_hotspots
from .explanation   import generate_explanation
from .chatbot       import chat_response
from .competitor    import analyze_competitor_impact
from .recommendation import generate_recommendations, generate_report
from .utils         import (
    haversine_distance,
    normalize,
    normalize_list,
    extract_features,
    get_weights,
    BUSINESS_WEIGHT_PRESETS,
    SAMPLE_LOCATION,
    SAMPLE_WEIGHTS,
)

__all__ = [
    # Scoring
    "calculate_score",
    "personalized_score",
    "compare_locations",
    # Clustering
    "detect_hotspots",
    # Explanation
    "generate_explanation",
    # Chatbot
    "chat_response",
    # Competitor
    "analyze_competitor_impact",
    # Recommendations & Report
    "generate_recommendations",
    "generate_report",
    # Utils
    "haversine_distance",
    "normalize",
    "normalize_list",
    "extract_features",
    "get_weights",
    "BUSINESS_WEIGHT_PRESETS",
    "SAMPLE_LOCATION",
    "SAMPLE_WEIGHTS",
]
