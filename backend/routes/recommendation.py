from fastapi import APIRouter, HTTPException
from services.ai_service import generate_recommendations

router = APIRouter()

@router.post("/get-recommendations")
async def get_recommendations():
    try:
        result = generate_recommendations()
        return {"recommendations": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
