"""
tests/test_ai_module.py — GeoVision AI
Integration tests for all AI module functions.
Run with: pytest tests/ -v
"""

from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from ai.utils import haversine_distance, normalize, normalize_list, extract_features, get_weights
from ai.scoring import calculate_score, compare_locations, personalized_score
from ai.clustering import detect_hotspots, SAMPLE_COORDINATES
from ai.explanation import generate_explanation
from ai.chatbot import chat_response
from ai.competitor import analyze_competitor_impact
from ai.recommendation import generate_recommendations, generate_report


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def base_location():
    return {
        "lat":           28.6139,
        "lng":           77.2090,
        "business_type": "retail",
        "population":    120_000,
        "competition":   8,
        "accessibility": 7.5,
        "footfall":      3_500,
        "avg_income":    65,
    }


@pytest.fixture
def weight_override():
    return {"population": 0.5, "competition": 0.3, "accessibility": 0.2}


# ============================================================================
# utils.py tests
# ============================================================================

class TestUtils:
    def test_haversine_known_distance(self):
        # Delhi → Mumbai ≈ 1148 km
        dist = haversine_distance(28.6139, 77.2090, 19.0760, 72.8777)
        assert 1100 < dist < 1200, f"Unexpected distance: {dist}"

    def test_haversine_same_point(self):
        assert haversine_distance(10.0, 10.0, 10.0, 10.0) == pytest.approx(0, abs=0.001)

    def test_normalize_in_range(self):
        assert normalize(5, 0, 10) == pytest.approx(0.5)
        assert normalize(0, 0, 10) == pytest.approx(0.0)
        assert normalize(10, 0, 10) == pytest.approx(1.0)

    def test_normalize_clamps(self):
        assert normalize(-5, 0, 10) == 0.0
        assert normalize(15, 0, 10) == 1.0

    def test_normalize_zero_range(self):
        assert normalize(5, 5, 5) == pytest.approx(0.5)

    def test_normalize_list(self):
        vals = [0.0, 5.0, 10.0]
        result = normalize_list(vals)
        assert result == [pytest.approx(0.0), pytest.approx(0.5), pytest.approx(1.0)]

    def test_extract_features_keys(self, base_location):
        features = extract_features(base_location)
        assert set(features.keys()) == {"population", "competition", "accessibility", "footfall", "avg_income"}

    def test_extract_features_range(self, base_location):
        features = extract_features(base_location)
        for v in features.values():
            assert 0.0 <= v <= 1.0, f"Feature out of range: {v}"

    def test_get_weights_sums_to_one(self):
        weights = get_weights("retail")
        assert sum(weights.values()) == pytest.approx(1.0, abs=0.01)

    def test_get_weights_custom_override(self, weight_override):
        weights = get_weights("retail", weight_override)
        assert sum(weights.values()) == pytest.approx(1.0, abs=0.01)

    def test_get_weights_unknown_type_falls_back(self):
        weights = get_weights("unknown_type")
        assert sum(weights.values()) == pytest.approx(1.0, abs=0.01)


# ============================================================================
# scoring.py tests
# ============================================================================

class TestScoring:
    def test_score_output_keys(self, base_location):
        result = calculate_score(base_location)
        assert "score" in result
        assert "factors" in result
        assert "grade" in result
        assert "business_type" in result

    def test_score_in_range(self, base_location):
        result = calculate_score(base_location)
        assert 0 <= result["score"] <= 100

    def test_score_is_int(self, base_location):
        result = calculate_score(base_location)
        assert isinstance(result["score"], int)

    def test_grade_consistent(self, base_location):
        result = calculate_score(base_location)
        score = result["score"]
        grade = result["grade"]
        expected = "A" if score >= 85 else "B" if score >= 70 else "C" if score >= 55 else "D" if score >= 40 else "F"
        assert grade == expected

    def test_high_competition_lowers_score(self, base_location):
        low_comp  = calculate_score({**base_location, "competition": 1})
        high_comp = calculate_score({**base_location, "competition": 40})
        assert low_comp["score"] > high_comp["score"]

    def test_custom_weights_accepted(self, base_location, weight_override):
        result = calculate_score({**base_location, "weights": weight_override})
        assert 0 <= result["score"] <= 100

    def test_personalized_score_returns_all_types(self, base_location):
        result = personalized_score(base_location)
        from ai.utils import BUSINESS_WEIGHT_PRESETS
        assert len(result["rankings"]) == len(BUSINESS_WEIGHT_PRESETS)
        assert "best_fit" in result

    def test_compare_locations_returns_winner(self, base_location):
        loc2 = {**base_location, "population": 10_000, "competition": 30}
        result = compare_locations([base_location, loc2])
        assert "comparison" in result
        assert "winner" in result
        assert len(result["comparison"]) == 2

    def test_compare_sorted_descending(self, base_location):
        loc2 = {**base_location, "population": 10_000}
        result = compare_locations([base_location, loc2])
        scores = [c["score"] for c in result["comparison"]]
        assert scores == sorted(scores, reverse=True)


# ============================================================================
# clustering.py tests
# ============================================================================

class TestClustering:
    def test_hotspot_output_keys(self):
        result = detect_hotspots(SAMPLE_COORDINATES)
        assert "hotspots" in result
        assert "total_clusters" in result
        assert "noise_points" in result

    def test_hotspot_finds_clusters(self):
        result = detect_hotspots(SAMPLE_COORDINATES, eps_km=1.5, min_samples=3)
        assert result["total_clusters"] >= 1

    def test_hotspot_intensity_in_range(self):
        result = detect_hotspots(SAMPLE_COORDINATES)
        for h in result["hotspots"]:
            assert 0.0 <= h["intensity"] <= 1.0

    def test_hotspot_empty_input(self):
        result = detect_hotspots([])
        assert result == {"hotspots": [], "total_clusters": 0, "noise_points": 0}

    def test_hotspot_single_point_is_noise(self):
        result = detect_hotspots(
            [{"lat": 0.0, "lng": 0.0}],
            eps_km=1.0,
            min_samples=2,
        )
        assert result["total_clusters"] == 0
        assert result["noise_points"] == 1


# ============================================================================
# explanation.py tests  (fallback only — no LLM key required)
# ============================================================================

class TestExplanation:
    def test_explanation_keys(self):
        result = generate_explanation(score=72, factors={
            "population": 0.7, "competition": 0.6,
            "accessibility": 0.8, "footfall": 0.5, "avg_income": 0.65,
        })
        assert "explanation" in result
        assert "strengths" in result
        assert "weaknesses" in result
        assert "opportunities" in result
        assert "risk_level" in result

    def test_risk_level_low_for_high_score(self):
        result = generate_explanation(score=90, factors={
            "population": 0.9, "competition": 0.85,
            "accessibility": 0.95, "footfall": 0.9, "avg_income": 0.85,
        })
        assert result["risk_level"] == "Low"

    def test_risk_level_high_for_low_score(self):
        result = generate_explanation(score=30, factors={
            "population": 0.2, "competition": 0.2,
            "accessibility": 0.3, "footfall": 0.15, "avg_income": 0.2,
        })
        assert result["risk_level"] == "High"

    def test_strengths_weaknesses_are_lists(self):
        result = generate_explanation(score=55, factors={
            "population": 0.5, "competition": 0.45, "accessibility": 0.6,
        })
        assert isinstance(result["strengths"],     list)
        assert isinstance(result["weaknesses"],    list)
        assert isinstance(result["opportunities"], list)


# ============================================================================
# chatbot.py tests  (fallback only)
# ============================================================================

class TestChatbot:
    def test_response_keys(self):
        result = chat_response("What makes a good retail location?")
        assert "response" in result
        assert "source" in result
        assert "suggestions" in result

    def test_empty_query_handled(self):
        result = chat_response("")
        assert result["response"] != ""

    def test_suggestions_is_list(self):
        result = chat_response("Tell me about foot traffic")
        assert isinstance(result["suggestions"], list)
        assert len(result["suggestions"]) > 0

    def test_context_injection(self):
        result = chat_response(
            "Should I open here?",
            context={"score": 72, "business_type": "retail", "lat": 28.6, "lng": 77.2},
        )
        assert "response" in result


# ============================================================================
# competitor.py tests
# ============================================================================

class TestCompetitor:
    def test_competitor_impact_keys(self, base_location):
        result = analyze_competitor_impact(base_location)
        assert "impact"             in result
        assert "score_change"       in result
        assert "score_with_comp"    in result
        assert "score_without_comp" in result
        assert "nearby_competitors" in result
        assert "risk_level"         in result

    def test_score_without_comp_gte_with_comp(self, base_location):
        result = analyze_competitor_impact(base_location)
        assert result["score_without_comp"] >= result["score_with_comp"]

    def test_no_nearby_competitors_low_risk(self, base_location):
        # Move to remote location with no sample competitors nearby
        remote = {**base_location, "lat": 0.0, "lng": 0.0}
        result = analyze_competitor_impact(remote, radius_km=1.0)
        assert result["nearby_competitors"] == 0
        assert result["risk_level"] == "Low"


# ============================================================================
# recommendation.py tests
# ============================================================================

class TestRecommendations:
    def test_recommendations_keys(self):
        result = generate_recommendations({"business_type": "retail"}, top_n=3)
        assert "locations"       in result
        assert "total_evaluated" in result
        assert "business_type"   in result

    def test_recommendations_count(self):
        result = generate_recommendations({"business_type": "retail"}, top_n=5)
        assert len(result["locations"]) <= 5
        assert len(result["locations"]) >= 1

    def test_recommendations_sorted(self):
        result = generate_recommendations({"business_type": "retail"})
        scores = [loc["score"] for loc in result["locations"]]
        assert scores == sorted(scores, reverse=True)

    def test_city_filter(self):
        result = generate_recommendations({"business_type": "retail"}, city_filter="Mumbai")
        for loc in result["locations"]:
            assert loc["city"].lower() == "mumbai"

    def test_min_score_filter(self):
        result = generate_recommendations({"business_type": "retail"}, min_score=70)
        for loc in result["locations"]:
            assert loc["score"] >= 70

    def test_report_generation(self, base_location):
        score_result = calculate_score(base_location)
        explanation  = generate_explanation(score=score_result["score"], factors=score_result["factors"])
        recs         = generate_recommendations({"business_type": "retail"}, top_n=3)
        report       = generate_report(score_result, explanation, recs, base_location)

        assert "report_version"       in report
        assert "generated_at"         in report
        assert "site_readiness"       in report
        assert "ai_explanation"       in report
        assert "top_recommendations"  in report
        assert "summary"              in report


# ============================================================================
# End-to-end flow test
# ============================================================================

class TestEndToEnd:
    def test_full_pipeline(self, base_location):
        """Simulate the complete frontend → AI flow."""
        # Step 1: Score
        score_result = calculate_score(base_location)
        assert 0 <= score_result["score"] <= 100

        # Step 2: Explanation
        explanation = generate_explanation(
            score=score_result["score"],
            factors=score_result["factors"],
            business_type="retail",
        )
        assert explanation["risk_level"] in ("Low", "Medium", "High")

        # Step 3: Recommendations
        recs = generate_recommendations({"business_type": "retail"}, top_n=3)
        assert len(recs["locations"]) >= 1

        # Step 4: Competitor impact
        comp = analyze_competitor_impact(base_location)
        assert "impact" in comp

        # Step 5: Hotspots
        hotspots = detect_hotspots(SAMPLE_COORDINATES)
        assert "hotspots" in hotspots

        # Step 6: Report
        report = generate_report(score_result, explanation, recs, base_location)
        assert report["site_readiness"]["score"] == score_result["score"]
