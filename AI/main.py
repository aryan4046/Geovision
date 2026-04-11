"""
main.py — GeoVision AI  ·  FastAPI Application
All endpoints follow the strict names defined in GeoVision_AI_Guideline.txt
"""

from __future__ import annotations

import os
from typing import Any, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# --- AI module imports -------------------------------------------------------
from ai.scoring       import calculate_score, compare_locations
from ai.clustering    import detect_hotspots, SAMPLE_COORDINATES
from ai.explanation   import generate_explanation
from ai.chatbot       import chat_response, Message
from ai.competitor    import analyze_competitor_impact
from ai.recommendation import generate_recommendations, generate_report

# =============================================================================
# App setup
# =============================================================================

app = FastAPI(
    title="GeoVision AI",
    description="AI-powered geospatial business intelligence platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — allow React frontend (adjust origins in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# Pydantic request / response models
# =============================================================================

# ── /get-score ────────────────────────────────────────────────────────────────
class WeightsModel(BaseModel):
    population:    float = Field(0.4,  ge=0, le=1)
    competition:   float = Field(0.35, ge=0, le=1)
    accessibility: float = Field(0.25, ge=0, le=1)


class ScoreRequest(BaseModel):
    lat:           float
    lng:           float
    business_type: str          = "retail"
    population:    float        = 50_000
    competition:   float        = 5
    accessibility: float        = 5.0
    footfall:      float        = 500
    avg_income:    float        = 50
    weights:       Optional[WeightsModel] = None


class ScoreResponse(BaseModel):
    score:         int
    factors:       dict[str, float]
    grade:         str
    business_type: str


# ── /get-recommendations ──────────────────────────────────────────────────────
class RecommendationRequest(BaseModel):
    business_type: str                    = "retail"
    weights:       Optional[WeightsModel] = None
    top_n:         int                    = Field(5, ge=3, le=10)
    city_filter:   Optional[str]          = None
    min_score:     int                    = Field(0, ge=0, le=100)


class RecommendationResponse(BaseModel):
    locations:       list[dict]
    total_evaluated: int
    business_type:   str


# ── /get-hotspots ─────────────────────────────────────────────────────────────
class HotspotPoint(BaseModel):
    lat:           float
    lng:           float
    population:    float = 50_000
    footfall:      float = 500
    accessibility: float = 5.0


class HotspotsResponse(BaseModel):
    hotspots:       list[dict]
    total_clusters: int
    noise_points:   int


# ── /get-explanation ──────────────────────────────────────────────────────────
class ExplanationRequest(BaseModel):
    score:         int
    factors:       dict[str, float]
    business_type: str = "business"


class ExplanationResponse(BaseModel):
    explanation:   str
    strengths:     list[str]
    weaknesses:    list[str]
    opportunities: list[str]
    risk_level:    str


# ── /chat ─────────────────────────────────────────────────────────────────────
class ChatRequest(BaseModel):
    query:   str
    history: list[Message] = []
    context: Optional[dict] = None


class ChatResponse(BaseModel):
    response:    str
    source:      str
    suggestions: list[str]


# ── /competitor-impact ────────────────────────────────────────────────────────
class CompetitorRequest(BaseModel):
    lat:           float
    lng:           float
    business_type: str   = "retail"
    population:    float = 50_000
    accessibility: float = 5.0
    footfall:      float = 500
    avg_income:    float = 50
    radius_km:     float = Field(2.0, gt=0, le=50)


class CompetitorResponse(BaseModel):
    impact:             str
    score_change:       int
    score_with_comp:    int
    score_without_comp: int
    nearby_competitors: int
    competitor_names:   list[str]
    risk_level:         str


# ── /compare ─────────────────────────────────────────────────────────────────
class CompareRequest(BaseModel):
    locations: list[dict]   # each element same shape as ScoreRequest


class CompareResponse(BaseModel):
    comparison: list[dict]
    winner:     dict


# ── /report ──────────────────────────────────────────────────────────────────
class ReportRequest(BaseModel):
    lat:           float
    lng:           float
    business_type: str                    = "retail"
    population:    float                  = 50_000
    competition:   float                  = 5
    accessibility: float                  = 5.0
    footfall:      float                  = 500
    avg_income:    float                  = 50
    weights:       Optional[WeightsModel] = None


# =============================================================================
# Health check
# =============================================================================

@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "service": "GeoVision AI", "version": "1.0.0"}


@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}


# =============================================================================
# POST /get-score   — Site Readiness Score + Personalized Scoring
# =============================================================================

@app.post("/get-score", response_model=ScoreResponse, tags=["Scoring"])
def get_score(body: ScoreRequest):
    """
    Calculate the Site Readiness Score for a location.
    Also handles Personalized Scoring Engine via business_type parameter.
    """
    try:
        payload = body.model_dump()
        if payload.get("weights"):
            payload["weights"] = body.weights.model_dump()
        result = calculate_score(payload)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# POST /get-recommendations   — Recommendation Engine
# =============================================================================

@app.post("/get-recommendations", response_model=RecommendationResponse, tags=["Recommendations"])
def get_recommendations(body: RecommendationRequest):
    """
    Return top-N ranked location recommendations for the given business type.
    """
    try:
        payload = body.model_dump()
        if payload.get("weights"):
            payload["weights"] = body.weights.model_dump()
        result = generate_recommendations(
            data=payload,
            top_n=body.top_n,
            city_filter=body.city_filter,
            min_score=body.min_score,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# GET /get-hotspots   — Hotspot Detection
# =============================================================================

@app.get("/get-hotspots", response_model=HotspotsResponse, tags=["Hotspots"])
def get_hotspots(
    eps_km:      float = Query(1.5, gt=0, description="Cluster radius in km"),
    min_samples: int   = Query(3,   ge=2, description="Min points per cluster"),
):
    """
    Detect geographic hotspots using DBSCAN on the default candidate dataset.
    In production, replace SAMPLE_COORDINATES with real DB query results.
    """
    try:
        result = detect_hotspots(
            coordinates=SAMPLE_COORDINATES,
            eps_km=eps_km,
            min_samples=min_samples,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/get-hotspots", response_model=HotspotsResponse, tags=["Hotspots"])
def get_hotspots_custom(
    body:        list[HotspotPoint],
    eps_km:      float = Query(1.5, gt=0),
    min_samples: int   = Query(3,   ge=2),
):
    """
    Detect hotspots from a custom set of coordinates provided in the request body.
    """
    try:
        coords = [p.model_dump() for p in body]
        result = detect_hotspots(coords, eps_km=eps_km, min_samples=min_samples)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# POST /get-explanation   — AI Explanation Engine
# =============================================================================

@app.post("/get-explanation", response_model=ExplanationResponse, tags=["Explanation"])
def get_explanation(body: ExplanationRequest):
    """
    Generate a natural-language explanation of a site readiness score using LLM.
    """
    try:
        result = generate_explanation(
            score=body.score,
            factors=body.factors,
            business_type=body.business_type,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# POST /chat   — AI Business Advisor Chatbot
# =============================================================================

@app.post("/chat", response_model=ChatResponse, tags=["Chatbot"])
def chat(body: ChatRequest):
    """
    AI Business Advisor — answer geospatial and business strategy questions.
    """
    try:
        if not body.query or not body.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty.")
        result = chat_response(
            query=body.query,
            history=body.history,
            context=body.context,
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# POST /competitor-impact   — Competitor Impact Analyzer
# =============================================================================

@app.post("/competitor-impact", response_model=CompetitorResponse, tags=["Competitors"])
def competitor_impact(body: CompetitorRequest):
    """
    Analyse how nearby competitors affect the site readiness score.
    """
    try:
        payload = body.model_dump()
        result  = analyze_competitor_impact(
            data=payload,
            radius_km=body.radius_km,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# POST /compare   — Location Comparison
# =============================================================================

@app.post("/compare", response_model=CompareResponse, tags=["Comparison"])
def compare(body: CompareRequest):
    """
    Compare multiple locations side-by-side; returns ranked scores and winner.
    """
    if not body.locations or len(body.locations) < 2:
        raise HTTPException(
            status_code=400,
            detail="Provide at least 2 locations for comparison.",
        )
    try:
        result = compare_locations(body.locations)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# POST /report   — Report Generation
# =============================================================================

@app.post("/report", tags=["Report"])
def report(body: ReportRequest):
    """
    Generate a full structured report combining score, explanation, and recommendations.
    """
    try:
        payload = body.model_dump()

        score_result   = calculate_score(payload)
        explanation    = generate_explanation(
            score=score_result["score"],
            factors=score_result["factors"],
            business_type=body.business_type,
        )
        recommendations = generate_recommendations(
            data={"business_type": body.business_type},
            top_n=3,
        )

        result = generate_report(
            score_result=score_result,
            explanation_result=explanation,
            recommendations=recommendations,
            input_data=payload,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Entry point
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
