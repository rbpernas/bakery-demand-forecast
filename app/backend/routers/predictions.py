"""
predictions.py
--------------
Endpoint to get demand predictions for a given day.
"""

import sqlite3
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.backend.database import get_db, DB_PATH
from src.models.rule_based import RuleBasedModel

router = APIRouter()


@router.get("/")
def get_predictions(
    target_date:      date  = Query(default_factory=date.today),
    is_holiday:       bool  = Query(default=False),
    is_local_event:   bool  = Query(default=False),
    temperature_max:  Optional[float] = Query(default=None),
    precipitation_mm: Optional[float] = Query(default=None),
    db: sqlite3.Connection = Depends(get_db),
):
    model = RuleBasedModel(db_path=DB_PATH)
    predictions = model.predict_all(
        target_date=target_date,
        is_holiday=is_holiday,
        is_local_event=is_local_event,
        temperature_max=temperature_max,
        precipitation_mm=precipitation_mm,
    )

    return [
        {
            "product":      p.product_name,
            "date":         p.target_date.isoformat(),
            "units":        p.units,
            "confidence":   p.confidence,
            "observations": p.observations,
            "breakdown":    p.breakdown,
        }
        for p in predictions
    ]