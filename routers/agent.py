from fastapi import APIRouter, HTTPException
from models.schemas import agentRequest
from services.llm import analyze_costs_multistep

router = APIRouter()

@router.post("/analyze")
async def analyze(request: agentRequest):
    try:
        summary_dict = {
            "current_month_total": request.summary.current_month_total,
            "previous_month_total": request.summary.previous_month_total,
            "percent_change": request.summary.percent_change,
            "avg_daily": request.summary.avg_daily,
            "forecasted_total": request.summary.forecasted_total,
            "top_spenders": request.summary.top_spenders
        }

        cost_list = [c.dict() for c in request.cost_data]

        result = analyze_costs_multistep(
            summary=summary_dict,
            cost_data=cost_list,
            goal=request.goal
        )

        return {"Success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))