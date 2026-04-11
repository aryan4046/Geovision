import sys, os
sys.path.append('.')
sys.path.append('./AI')

from backend.services.data_service import get_population_density, get_nearby_competitors, get_nearby_pois, get_accessibility_score
from backend.services.ai_service import calculate_score, generate_explanation, analyze_competitor_impact

def test_location(lat, lng, label, business_type="restaurant"):
    print("\n=== Testing: %s (%.4f, %.4f) ===" % (label, lat, lng))
    pop  = get_population_density(lat, lng)
    comp = get_nearby_competitors(lat, lng)
    pois = get_nearby_pois(lat, lng)
    acc  = get_accessibility_score(pois)
    print("  pop=%.0f  competitors=%d  pois=%d  accessibility=%.1f" % (pop, len(comp), len(pois), acc))

    weights = {"population": 0.4, "competition": 0.35, "accessibility": 0.25}
    result = calculate_score(lat, lng, pop, comp, pois, acc, business_type, weights)
    score   = result["score"]
    grade   = result["grade"]
    factors = result["factors"]
    print("  Score=%d  Grade=%s" % (score, grade))
    print("  pop_factor=%.2f  comp_factor=%.2f  access_factor=%.2f  footfall=%.2f" % (
        factors.get("population", 0),
        factors.get("competition", 0),
        factors.get("accessibility", 0),
        factors.get("footfall", 0),
    ))

    expl = generate_explanation(score, factors, business_type)
    print("  Risk: %s | Strengths: %d | Weaknesses: %d" % (
        expl["risk_level"], len(expl["strengths"]), len(expl["weaknesses"])))

# Test the Sanand area from the screenshot (sparse rural area)
test_location(23.0540, 72.3711, "Sanand / Ahmedabad Rural", "restaurant")

# Test Delhi CP (dense urban)
test_location(28.6315, 77.2167, "Delhi - Connaught Place", "restaurant")

# Test remote area (middle of India — no nearby data)
test_location(22.0, 79.0, "Remote India (no nearby city)", "retail")

print("\n=== ALL SYSTEMS OPERATIONAL ===")
