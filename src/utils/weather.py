"""
weather.py
----------
Fetches weather forecast data from Open-Meteo (free, no API key required).
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Optional

import requests

LATITUDE  = 40.2317
LONGITUDE =  0.0736

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

DAILY_VARIABLES = [
    "temperature_2m_max",
    "precipitation_sum",
]


def get_forecast(target_date: Optional[date] = None) -> dict:
    if target_date is None:
        target_date = date.today() + timedelta(days=1)

    date_str = target_date.isoformat()

    try:
        import certifi
        url = (
            f"{OPEN_METEO_URL}"
            f"?latitude={LATITUDE}"
            f"&longitude={LONGITUDE}"
            f"&daily=temperature_2m_max,precipitation_sum"
            f"&timezone=Europe%2FMadrid"
            f"&forecast_days=7"
        )
        response = requests.get(url, verify=False, timeout=5)
        response.raise_for_status()
        data = response.json()

        daily  = data.get("daily", {})
        dates  = daily.get("time", [])
        temps  = daily.get("temperature_2m_max", [])
        precips = daily.get("precipitation_sum", [])

        # Find the index matching our target date
        idx = dates.index(date_str) if date_str in dates else 0
        temp   = temps[idx]   if idx < len(temps)   else None
        precip = precips[idx] if idx < len(precips) else None

        return {
            "date":             date_str,
            "temperature_max":  round(temp,   1) if temp   is not None else None,
            "precipitation_mm": round(precip, 1) if precip is not None else None,
            "available":        True,
        }

    except Exception as e:
        print(f"Weather API error: {e}")
        return {
            "date":             date_str,
            "temperature_max":  None,
            "precipitation_mm": None,
            "available":        False,
        }