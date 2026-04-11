from pydantic import BaseModel
from typing import Dict, List, Any, Optional

class LocationRequest(BaseModel):
    lat: float
    lng: float
    business_type: str
    weights: Dict[str, float]

class ChatRequest(BaseModel):
    message: str
    context: Optional[Any] = None

class ExplanationRequest(BaseModel):
    lat: float
    lng: float
    business_type: str = "retail"

class CompetitorRequest(BaseModel):
    lat: float
    lng: float

class LocationData(BaseModel):
    lat: float
    lng: float

class CompareRequest(BaseModel):
    location1: LocationData
    location2: LocationData
