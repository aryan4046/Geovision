from fastapi import APIRouter, HTTPException
from services.ai_service import run_dbscan

router = APIRouter()

@router.get("/get-hotspots")
async def get_hotspots():
    try:
        result = run_dbscan()
        return {"clusters": result} if not isinstance(result, dict) else result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
