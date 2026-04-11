from pydantic import BaseModel
from typing import Dict, Any, List, Optional

class ScoreResponse(BaseModel):
    score: int
    factors: Dict[str, Any]

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
