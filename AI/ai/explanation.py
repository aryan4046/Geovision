"""
explanation.py — GeoVision AI
AI Explanation Engine — generates human-readable location insight via LLM.
Endpoint: POST /get-explanation
"""

from __future__ import annotations

import os
import json
from typing import Any

# ---------------------------------------------------------------------------
# LLM client bootstrap (Groq — OpenAI-compatible)
# ---------------------------------------------------------------------------

def _get_llm_client():
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key:
        try:
            import openai  # type: ignore
            return openai.OpenAI(
                api_key=groq_key,
                base_url="https://api.groq.com/openai/v1",
            )
        except ImportError:
            pass
    return None


# ---------------------------------------------------------------------------
# Prompt builder
# ---------------------------------------------------------------------------

def _build_explanation_prompt(score: int, factors: dict, business_type: str = "business") -> str:
    factors_str = "\n".join(
        f"  - {k.replace('_', ' ').title()}: {round(v * 100, 1)}%"
        for k, v in factors.items()
    )
    
    weakness_rule = (
        "- You MUST provide legitimate weaknesses as the score is below 75." if score < 75 else
        "- The score is 75 or higher. Only list a weakness if genuinely supported by the data (e.g. clearly low percentage). Otherwise, return an empty array [] for weaknesses."
    )

    return f"""
You are GeoVision AI, an expert geospatial business intelligence assistant.

A location has been analysed for a {business_type} with a Site Readiness Score of {score}/100.

Factor breakdown (normalised 0-1 → shown as %):
{factors_str}

Please provide a structured analysis in STRICT JSON with this exact schema:
{{
  "explanation": "<2-3 sentence summary of why this location received this score>",
  "strengths": ["<strength 1>", "<strength 2>"],
  "weaknesses": ["<weakness 1>"],
  "opportunities": ["<opportunity 1>"],
  "risk_level": "<Low | Medium | High>"
}}

Rules:
- Be specific and data-driven focusing squarely on advantages and true data.
- {weakness_rule}
- Strengths and opportunities MUST reflect the real data advantages shown in the Factor breakdown.
- Return ONLY valid JSON, no markdown fences.
""".strip()


# ---------------------------------------------------------------------------
# Core function
# ---------------------------------------------------------------------------

def generate_explanation(
    score: int,
    factors: dict[str, float],
    business_type: str = "business",
) -> dict[str, Any]:
    """
    Generate a natural-language explanation of a site readiness score.

    Parameters
    ----------
    score        : int   — 0-100 site readiness score
    factors      : dict  — normalised factor values (0-1)
    business_type: str   — type of business for contextual explanation

    Returns
    -------
    dict
        {
            "explanation":   str,
            "strengths":     list[str],
            "weaknesses":    list[str],
            "opportunities": list[str],
            "risk_level":    str
        }
    """
    prompt = _build_explanation_prompt(score, factors, business_type)
    client   = _get_llm_client()
    raw_text = None

    try:
        if client:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                max_tokens=800,
                temperature=0.7,
                messages=[
                    {"role": "system", "content": "You are GeoVision AI, a geospatial business intelligence expert."},
                    {"role": "user",   "content": prompt},
                ],
            )
            raw_text = response.choices[0].message.content

    except Exception as exc:
        return _fallback_explanation(score, factors, error=str(exc))

    if not raw_text:
        return _fallback_explanation(score, factors)

    # Parse JSON from LLM output
    try:
        # Strip accidental markdown fences
        cleaned = raw_text.strip().strip("```json").strip("```").strip()
        result  = json.loads(cleaned)

        # Ensure all required keys are present
        result.setdefault("explanation",   "No explanation generated.")
        result.setdefault("strengths",     [])
        result.setdefault("weaknesses",    [])
        result.setdefault("opportunities", [])
        result.setdefault("risk_level",    _derive_risk(score))
        return result

    except json.JSONDecodeError:
        # LLM returned plain text: wrap it
        return {
            "explanation":   raw_text[:500],
            "strengths":     _derive_strengths(factors),
            "weaknesses":    _derive_weaknesses(factors, score),
            "opportunities": ["Explore infrastructure investment", "Target underserved demographics"],
            "risk_level":    _derive_risk(score),
        }


# ---------------------------------------------------------------------------
# Rule-based fallback (no API key or LLM error)
# ---------------------------------------------------------------------------

def _derive_risk(score: int) -> str:
    if score >= 75:
        return "Low"
    if score >= 50:
        return "Medium"
    return "High"


def _derive_strengths(factors: dict) -> list[str]:
    strengths = []
    if factors.get("population", 0) > 0.6:
        strengths.append("High population density supports strong customer base")
    if factors.get("accessibility", 0) > 0.6:
        strengths.append("Excellent transport and road accessibility")
    if factors.get("competition", 0) > 0.6:
        strengths.append("Low competitive saturation in the area")
    if factors.get("footfall", 0) > 0.6:
        strengths.append("High pedestrian footfall drives walk-in traffic")
    if factors.get("avg_income", 0) > 0.6:
        strengths.append("Above-average household income in catchment area")
    return strengths or ["Moderate market conditions present baseline opportunities"]


def _derive_weaknesses(factors: dict, score: int = 50) -> list[str]:
    weaknesses = []
    if factors.get("population", 1) < 0.4:
        weaknesses.append("Sparse population limits addressable market size")
    if factors.get("accessibility", 1) < 0.4:
        weaknesses.append("Poor road or transit connectivity may deter customers")
    if factors.get("competition", 1) < 0.4:
        weaknesses.append("High competitor density could suppress market share")
    if factors.get("footfall", 1) < 0.4:
        weaknesses.append("Low footfall reduces spontaneous discovery potential")
        
    if not weaknesses and score < 75:
        return ["Limited data available for complete risk assessment"]
    return weaknesses


def _fallback_explanation(
    score: int,
    factors: dict,
    error: str | None = None,
) -> dict[str, Any]:
    note = f" (LLM unavailable: {error})" if error else " (rule-based fallback)"
    return {
        "explanation":   (
            f"This location received a Site Readiness Score of {score}/100.{note} "
            f"The score reflects the weighted combination of population density, "
            f"competitive landscape, and accessibility metrics."
        ),
        "strengths":     _derive_strengths(factors),
        "weaknesses":    _derive_weaknesses(factors, score),
        "opportunities": [
            "Leverage local demographics for targeted marketing",
            "Consider partnerships to offset competitive pressure",
        ],
        "risk_level":    _derive_risk(score),
    }


# ---------------------------------------------------------------------------
# Quick self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    result = generate_explanation(
        score=72,
        factors={
            "population":    0.74,
            "competition":   0.55,
            "accessibility": 0.82,
            "footfall":      0.60,
            "avg_income":    0.70,
        },
        business_type="retail",
    )
    import json as _json
    print(_json.dumps(result, indent=2))
