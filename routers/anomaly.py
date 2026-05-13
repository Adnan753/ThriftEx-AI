from fastapi import APIRouter, HTTPException
from models.schemas import anomalyRequest
from services.anomaly_service import detect_anomalies

router = APIRouter()

@router.post("/detect")
async def detect(request: anomalyRequest):
    try:
        cost_list = [c.dict() for c in request.cost_data]
        result = detect_anomalies(cost_list)
        return {"Success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))