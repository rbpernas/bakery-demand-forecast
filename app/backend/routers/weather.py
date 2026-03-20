"""
weather.py (router)
-------------------
Endpoint to fetch weather forecast for the bakery location.

GET /weather?date=2024-06-17   — forecast for a specific date
GET /weather                   — forecast for tomorrow (default)
"""

from datetime import date
from typing import Optional

from fastapi import APIRouter, Query

from src.utils.weather import get_forecast

router = APIRouter()


@router.get("/")
def get_weather(
    target_date: Optional[date] = Query(default=None)
):
    return get_forecast(target_date)