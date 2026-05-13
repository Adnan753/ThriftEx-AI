import numpy as np
import pandas as pd
from collections import defaultdict

def forecast_costs(cost_data: list, days_ahead: int = 30) -> dict:

    daily_totals = defaultdict(float)
    for entry in cost_data:
        daily_totals[entry['date']] += entry['cost_amount']

    if len(daily_totals) < 10:
        return {"error": "Need at least 10 days of data for forecasting."}

    df = pd.DataFrame([
        {"ds": pd.to_datetime(date), "y": total}
        for date, total in sorted(daily_totals.items())
    ]).reset_index(drop=True)

    # Numeric index for regression
    x = np.arange(len(df))
    y = df["y"].values

    # Fit linear trend
    coeffs = np.polyfit(x, y, 1)
    trend = np.poly1d(coeffs)

    # Weekly seasonality: average residual per weekday
    df["weekday"] = df["ds"].dt.weekday
    df["residual"] = y - trend(x)
    seasonal = df.groupby("weekday")["residual"].mean().to_dict()

    # Generate forecast
    last_date = df["ds"].max()
    forecast = []
    for i in range(1, days_ahead + 1):
        future_date = last_date + pd.Timedelta(days=i)
        x_future = len(df) - 1 + i
        yhat = trend(x_future) + seasonal.get(future_date.weekday(), 0)
        yhat = max(yhat, 0)
        # Simple confidence interval: ±1 std of residuals
        std = float(df["residual"].std())
        forecast.append({
            "date": future_date.strftime("%Y-%m-%d"),
            "predicted": round(float(yhat), 6),
            "lower": round(max(float(yhat) - std, 0), 6),
            "upper": round(float(yhat) + std, 6)
        })

    predicted_values = [f["predicted"] for f in forecast]
    return {
        "forecast": forecast,
        "summary": {
            "days_forecasted": days_ahead,
            "avg_predicted_daily": round(float(np.mean(predicted_values)), 6),
            "total_predicted": round(float(np.sum(predicted_values)), 6)
        }
    }
