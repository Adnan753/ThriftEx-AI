import numpy as np
from collections import defaultdict

def detect_anomalies(cost_data: list) -> dict:

    daily_totals = defaultdict(float)
    for entry in cost_data:
        daily_totals[entry['date']] += entry['cost_amount']

    if len(daily_totals) < 3:
        return {"anomalies": [], "message": "Not enough data."}
    
    dates = sorted(daily_totals.keys())
    values = [daily_totals[d] for d in dates]

    mean = np.mean(values)
    std = np.std(values)

    anomalies = []
    for date, value in zip(dates, values):
        if std > 0:
            z_score = (value - mean) / std
            if abs(z_score) > 2:  # Threshold for anomaly
                anomalies.append({
                    "date": date,
                    "cost": round(value, 6),
                    "z_score": round(z_score, 2),
                    "severity": "high" if abs(z_score) > 3 else "medium",
                    "type": "spike" if z_score > 0 else "drop",
                    "deviation_percentage": round((value - mean) / mean * 100, 2)
                })

    return {
        "anomalies": anomalies,
        "stats": {
            "mean_daily": round(mean, 6),
            "std_dev": round(std, 6),
            "total_days_analyzed": len(dates)
        }
    }