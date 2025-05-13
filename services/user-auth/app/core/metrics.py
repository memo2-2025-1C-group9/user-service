from functools import wraps
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

    requests.post(url, headers=headers, json=payload)


def metric_trace(action_name):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            send_metric(f"user_service.{action_name}_attempt")
            try:
                result = func(*args, **kwargs)
                send_metric(f"user_service.{action_name}_success")
                return result
            except Exception:
                send_metric(f"user_service.{action_name}_error")
                raise

        return wrapper

    return decorator
