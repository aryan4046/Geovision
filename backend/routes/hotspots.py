from fastapi import APIRouter, HTTPException
from services.ai_service import run_dbscan
from services.data_service import get_all_locations
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Use our rich population database as the coordinate source for clustering
HOTSPOT_SEED_COORDS = [
    {"lat": 28.6315, "lng": 77.2167, "population": 180000, "footfall": 8000, "accessibility": 9.2},
    {"lat": 28.5631, "lng": 77.2376, "population": 140000, "footfall": 5500, "accessibility": 7.8},
    {"lat": 28.5921, "lng": 77.0460, "population": 160000, "footfall": 4200, "accessibility": 8.5},
    {"lat": 28.5244, "lng": 77.2066, "population": 120000, "footfall": 6000, "accessibility": 8.0},
    {"lat": 28.6519, "lng": 77.1909, "population": 155000, "footfall": 5200, "accessibility": 7.5},
    {"lat": 28.7041, "lng": 77.1025, "population": 135000, "footfall": 4500, "accessibility": 7.0},
    {"lat": 19.0596, "lng": 72.8295, "population": 200000, "footfall": 9000, "accessibility": 8.8},
    {"lat": 19.1136, "lng": 72.8697, "population": 220000, "footfall": 8500, "accessibility": 9.0},
    {"lat": 19.2183, "lng": 72.9781, "population": 190000, "footfall": 6000, "accessibility": 7.5},
    {"lat": 19.0218, "lng": 72.8428, "population": 210000, "footfall": 8000, "accessibility": 8.0},
    {"lat": 19.1176, "lng": 72.9060, "population": 165000, "footfall": 5500, "accessibility": 7.8},
    {"lat": 12.9352, "lng": 77.6245, "population": 150000, "footfall": 7000, "accessibility": 7.2},
    {"lat": 12.9698, "lng": 77.7499, "population": 130000, "footfall": 5000, "accessibility": 7.8},
    {"lat": 12.9784, "lng": 77.6408, "population": 140000, "footfall": 6500, "accessibility": 8.0},
    {"lat": 13.0035, "lng": 77.5708, "population": 145000, "footfall": 5800, "accessibility": 7.6},
    {"lat": 17.4504, "lng": 78.3808, "population": 160000, "footfall": 7000, "accessibility": 8.5},
    {"lat": 17.4126, "lng": 78.4460, "population": 110000, "footfall": 5000, "accessibility": 7.0},
    {"lat": 17.4239, "lng": 78.4127, "population": 125000, "footfall": 5500, "accessibility": 7.3},
    {"lat": 18.5362, "lng": 73.8951, "population": 100000, "footfall": 4500, "accessibility": 7.5},
    {"lat": 18.5679, "lng": 73.9143, "population": 110000, "footfall": 4800, "accessibility": 8.0},
    {"lat": 13.0418, "lng": 80.2341, "population": 170000, "footfall": 7500, "accessibility": 8.2},
    {"lat": 13.0850, "lng": 80.2101, "population": 145000, "footfall": 6000, "accessibility": 7.8},
    {"lat": 22.5546, "lng": 88.3515, "population": 165000, "footfall": 6500, "accessibility": 7.5},
    {"lat": 22.5958, "lng": 88.4197, "population": 120000, "footfall": 5000, "accessibility": 7.2},
    {"lat": 28.5703, "lng": 77.3219, "population": 145000, "footfall": 6000, "accessibility": 8.0},
    {"lat": 28.4965, "lng": 77.0880, "population": 140000, "footfall": 7000, "accessibility": 8.5},
]

router = APIRouter()

@router.get("/get-hotspots")
async def get_hotspots():
    try:
        result = run_dbscan(HOTSPOT_SEED_COORDS)
        # result is {"hotspots": [...], "total_clusters": int, "noise_points": int}
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
