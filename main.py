from fastapi import FastAPI
from routers import agent, forecast, anomaly
from dotenv import load_dotenv

load_dotenv()

app = FastAPI (
    title="ThriftEx Agent",
    description="Agentic FinOps Intelligence Engine",
    version="1.0.0"
)

app.include_router(agent.router, prefix="/agent", tags=["Agent"])
app.include_router(forecast.router, prefix="/forecast", tags=["Forecast"])
app.include_router(anomaly.router, prefix="/anomaly", tags=["Anomaly"])

@app.get("/")
async def health():
    return {
        "status": "running",
        "service": "ThriftEx Agent",
        "version": "1.0.0"
    }
    