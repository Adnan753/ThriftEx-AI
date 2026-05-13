from fastapi import APIRouter, HTTPException
from models.schemas import forecastRequest
from services.prophet_service import forecast_costs

router = APIRouter()

@router.post('/predict')
async def predict(request: forecastRequest):
    try:
        cost_list = [c.dict() for c in request.cost_data]
        result = forecast_costs(cost_list, days_ahead=request.days_ahead)
        return {"Success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))