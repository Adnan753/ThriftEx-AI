from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class costEntry(BaseModel):
    date: str
    service: str
    cost_amount: float
    currency: str = "USD"

class costSummary(BaseModel):
    current_month_total: float
    previous_month_total: float
    percent_change: str
    avg_daily: float
    forecasted_total: float
    top_spenders: List[dict]

class agentRequest(BaseModel):
    cost_data: List[costEntry]
    summary: costSummary
    goal: Optional[str] = None

class anomalyRequest(BaseModel):
    cost_data: List[costEntry]

class forecastRequest(BaseModel):
    cost_data: List[costEntry]
    days_ahead: int = 30