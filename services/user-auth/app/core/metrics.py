from app.core.config import settings
import requests
import time


def send_metric(metric):
    url = settings.DATADOG_URL
    headers = {
        "Content-Type": "application/json",
        "DD-API-KEY": settings.DATADOG_API_KEY,
    }

    payload = {
        "series": [
            {
                "metric": metric,
                "points": [[int(time.time()), 1]],
                "type": "count",
                "interval": 1,
                "tags": ["env:production", "service:auth-service"],
                "host": "auth-service",
            }
        ]
    }

    response = requests.post(url, headers=headers, json=payload)
    print(f"Metric sent: {metric}, Response: {response.status_code}")
