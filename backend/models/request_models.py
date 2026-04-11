from pydantic import BaseModel
from typing import Dict, List, Any, Optional

class LocationRequest(BaseModel):
    lat: float
    lng: float
    business_type: str
    weights: Dict[str, float]

class ChatRequest(BaseModel):
    query: str

class CompareRequest(BaseModel):
    locations: List[Dict[str, Any]]
