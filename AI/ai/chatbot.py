"""
chatbot.py — GeoVision AI
AI Business Advisor Chatbot — answers geospatial business questions via LLM.
Endpoint: POST /chat
"""

from __future__ import annotations

import os
from typing import Any

# ---------------------------------------------------------------------------
# LLM client bootstrap (Groq — OpenAI-compatible)
# ---------------------------------------------------------------------------

def _get_llm_client():
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
        
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
# System prompt
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """
You are GeoVision AI Business Advisor, an expert assistant specialising in:
- Geospatial business intelligence
- Site selection and location strategy
- Market analysis and competitor assessment
- Urban planning and footfall analytics
- Business viability evaluation for retail, hospitality, healthcare, and more

Respond in a clear, concise, and professional tone.
When asked about a specific location, reference quantitative factors like
population density, accessibility scores, competitor count, and footfall.
Keep answers under 300 words unless a deeper analysis is specifically requested.
Do NOT make up specific data that wasn't provided — state assumptions clearly.
""".strip()


# ---------------------------------------------------------------------------
# Conversation history type
# ---------------------------------------------------------------------------

Message = dict[str, str]  # {"role": "user"|"assistant", "content": str}


# ---------------------------------------------------------------------------
# Core chatbot function
# ---------------------------------------------------------------------------

def chat_response(
    query: str,
    history: list[Message] | None = None,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Generate an AI response to a business / geospatial query.

    Parameters
    ----------
    query   : str            — user's question
    history : list[Message]  — previous conversation turns (optional)
    context : dict           — optional location context to inject
                               e.g. {"score": 72, "business_type": "retail", "lat": 28.6, "lng": 77.2}

    Returns
    -------
    dict
        {
            "response":     str,
            "source":       "claude" | "openai" | "fallback",
            "suggestions":  list[str]   # follow-up question suggestions
        }
    """
    if not query or not query.strip():
        return {
            "response":    "Please ask a question about a location or business strategy.",
            "source":      "fallback",
            "suggestions": _default_suggestions(),
        }

    # Build message list
    messages: list[Message] = list(history or [])

    # Inject location context if provided
    if context:
        ctx_lines = "\n".join(f"  {k}: {v}" for k, v in context.items())
        ctx_note  = f"[Current location context:\n{ctx_lines}]"
        # Prepend context as a user message only if history is empty
        if not messages:
            messages.append({"role": "user",      "content": ctx_note})
            messages.append({"role": "assistant",  "content": "Understood. I have the location context. How can I help?"})

    messages.append({"role": "user", "content": query})

    client = _get_llm_client()
    raw_text = None

    try:
        if client:
            full_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages
            resp = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                max_tokens=600,
                messages=full_messages,
            )
            raw_text = resp.choices[0].message.content

    except Exception as exc:
        return {
            "response":    f"I'm sorry, I encountered an error processing your request. ({exc})",
            "source":      "fallback",
            "suggestions": _default_suggestions(),
        }

    if not raw_text:
        return _fallback_response(query)

    return {
        "response":    raw_text.strip(),
        "source":      "openai",
        "suggestions": _generate_suggestions(query),
    }


# ---------------------------------------------------------------------------
# Suggestion helpers
# ---------------------------------------------------------------------------

def _default_suggestions() -> list[str]:
    return [
        "What makes a location ideal for a restaurant?",
        "How does competitor density affect my score?",
        "Which city in India has the best retail potential?",
        "What accessibility factors should I consider for a hospital?",
    ]


def _generate_suggestions(query: str) -> list[str]:
    q = query.lower()

    if "restaurant" in q or "food" in q:
        return [
            "What foot-traffic patterns favour restaurants?",
            "How many competitors are too many for a new café?",
            "Which time zones have peak dining footfall?",
        ]
    if "retail" in q or "shop" in q or "store" in q:
        return [
            "What population density is ideal for retail?",
            "How can I reduce the impact of nearby mall competition?",
            "What accessibility score should I aim for?",
        ]
    if "score" in q or "readiness" in q:
        return [
            "How is the Site Readiness Score calculated?",
            "What factors have the most weight in my score?",
            "How can I improve my location's score?",
        ]
    return _default_suggestions()


def _fallback_response(query: str) -> dict[str, Any]:
    return {
        "response": (
            "I'm currently operating in offline mode without an LLM connection. "
            "Please ensure ANTHROPIC_API_KEY or OPENAI_API_KEY is set. "
            f'Your question was: "{query}"'
        ),
        "source":      "fallback",
        "suggestions": _default_suggestions(),
    }


# ---------------------------------------------------------------------------
# Quick self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import json

    result = chat_response(
        query="Should I open a café near Connaught Place, Delhi?",
        context={"score": 78, "business_type": "restaurant", "lat": 28.6315, "lng": 77.2167},
    )
    print(json.dumps(result, indent=2))
