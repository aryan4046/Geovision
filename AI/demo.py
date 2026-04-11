"""
demo.py — GeoVision AI
Runs all AI module functions with dummy data and prints formatted output.
No server required. Run with: python3 demo.py
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(__file__))

# Load .env file so OPENAI_API_KEY is available
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from ai.scoring        import calculate_score, compare_locations, personalized_score
from ai.clustering     import detect_hotspots, SAMPLE_COORDINATES
from ai.explanation    import generate_explanation
from ai.chatbot        import chat_response
from ai.competitor     import analyze_competitor_impact
from ai.recommendation import generate_recommendations, generate_report

SEP = "\n" + "═" * 60 + "\n"

# ─────────────────────────────────────────────
# DUMMY DATA
# ─────────────────────────────────────────────
DUMMY_LOCATION = {
    "lat":           28.6139,
    "lng":           77.2090,
    "business_type": "retail",
    "population":    120_000,
    "competition":   8,
    "accessibility": 7.5,
    "footfall":      3_500,
    "avg_income":    65,
    "weights": {
        "population":    0.40,
        "competition":   0.35,
        "accessibility": 0.25,
    },
}

DUMMY_LOCATION_2 = {
    "lat":           19.0760,
    "lng":           72.8777,
    "business_type": "restaurant",
    "population":    200_000,
    "competition":   15,
    "accessibility": 9.0,
    "footfall":      8_000,
    "avg_income":    72,
}

# ─────────────────────────────────────────────
# 1. SITE READINESS SCORE
# ─────────────────────────────────────────────
print(SEP)
print("1️⃣   SITE READINESS SCORE  (POST /get-score)")
print(SEP)
score_result = calculate_score(DUMMY_LOCATION)
print(json.dumps(score_result, indent=2))

# ─────────────────────────────────────────────
# 2. PERSONALIZED SCORING ENGINE
# ─────────────────────────────────────────────
print(SEP)
print("2️⃣   PERSONALIZED SCORING ENGINE  (all business types)")
print(SEP)
personal = personalized_score(DUMMY_LOCATION)
print(f"Best fit: {personal['best_fit']}\n")
for r in personal["rankings"]:
    bar = "█" * (r["score"] // 5)
    print(f"  [{r['grade']}] {r['business_type']:<14}  {r['score']:>3}/100  {bar}")

# ─────────────────────────────────────────────
# 3. LOCATION COMPARISON
# ─────────────────────────────────────────────
print(SEP)
print("3️⃣   LOCATION COMPARISON  (POST /compare)")
print(SEP)
comparison = compare_locations([DUMMY_LOCATION, DUMMY_LOCATION_2])
print(json.dumps(comparison, indent=2))

# ─────────────────────────────────────────────
# 4. HOTSPOT DETECTION
# ─────────────────────────────────────────────
print(SEP)
print("4️⃣   HOTSPOT DETECTION  (GET /get-hotspots)")
print(SEP)
hotspots = detect_hotspots(SAMPLE_COORDINATES, eps_km=1.5, min_samples=3)
print(f"Total clusters : {hotspots['total_clusters']}")
print(f"Noise points   : {hotspots['noise_points']}")
print(f"Hotspots found : {len(hotspots['hotspots'])}\n")
for h in hotspots["hotspots"]:
    bar = "█" * int(h["intensity"] * 20)
    print(f"  Cluster {h['cluster_id']}  ({h['lat']}, {h['lng']})  intensity={h['intensity']}  pts={h['point_count']}  {bar}")

# ─────────────────────────────────────────────
# 5. AI EXPLANATION ENGINE
# ─────────────────────────────────────────────
print(SEP)
print("5️⃣   AI EXPLANATION ENGINE  (POST /get-explanation)")
print(SEP)
explanation = generate_explanation(
    score=score_result["score"],
    factors=score_result["factors"],
    business_type="retail",
)
print(json.dumps(explanation, indent=2))

# ─────────────────────────────────────────────
# 6. RECOMMENDATION ENGINE
# ─────────────────────────────────────────────
print(SEP)
print("6️⃣   RECOMMENDATION ENGINE  (POST /get-recommendations)")
print(SEP)
recs = generate_recommendations(
    data={"business_type": "retail"},
    top_n=5,
)
print(f"Evaluated {recs['total_evaluated']} locations → Top {len(recs['locations'])} results:\n")
for i, loc in enumerate(recs["locations"], 1):
    print(f"  {i}. [{loc['grade']}] {loc['name']:<20} {loc['city']:<12}  Score: {loc['score']}/100")

# ─────────────────────────────────────────────
# 7. COMPETITOR IMPACT ANALYZER
# ─────────────────────────────────────────────
print(SEP)
print("7️⃣   COMPETITOR IMPACT ANALYZER  (POST /competitor-impact)")
print(SEP)
comp_impact = analyze_competitor_impact(DUMMY_LOCATION)
print(json.dumps(comp_impact, indent=2))

# ─────────────────────────────────────────────
# 8. CHATBOT (offline fallback — no API key)
# ─────────────────────────────────────────────
print(SEP)
print("8️⃣   AI BUSINESS ADVISOR CHATBOT  (POST /chat)")
print(SEP)
chat = chat_response(
    query="Should I open a retail store near Connaught Place, Delhi?",
    context={"score": score_result["score"], "business_type": "retail", "lat": 28.6139, "lng": 77.2090},
)
print(f"Source   : {chat['source']}")
print(f"Response : {chat['response']}")
print(f"Suggestions:")
for s in chat["suggestions"]:
    print(f"  • {s}")

# ─────────────────────────────────────────────
# 9. REPORT GENERATION
# ─────────────────────────────────────────────
print(SEP)
print("9️⃣   REPORT GENERATION  (POST /report)")
print(SEP)
report = generate_report(
    score_result=score_result,
    explanation_result=explanation,
    recommendations=recs,
    input_data=DUMMY_LOCATION,
)
print(json.dumps(report, indent=2))

print(SEP)
print("✅  All GeoVision AI modules tested successfully with dummy data!")
print(SEP)
