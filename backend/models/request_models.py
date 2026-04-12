from pydantic import BaseModel
from typing import Dict, List, Any, Optional

class LocationRequest(BaseModel):
    lat: float
    lng: float
    business_type: str
    weights: Dict[str, float]
    location_name: Optional[str] = None

class ChatRequest(BaseModel):
    message: str
    context: Optional[Any] = None
    history: Optional[List[Dict[str, str]]] = None

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
    name: Optional[str] = None

class CompareRequest(BaseModel):
    location1: LocationData
    location2: LocationData
    business_type: str = "retail"
    weights: Dict[str, float] = {}
