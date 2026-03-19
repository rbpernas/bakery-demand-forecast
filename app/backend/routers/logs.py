"""
logs.py
-------
Endpoints for daily production and sales logging.
"""

import sqlite3
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, model_validator

from app.backend.database import get_db

router = APIRouter()


class DailyLogEntry(BaseModel):
    date:             date
    product_id:       int
    units_produced:   int
    units_sold:       int
    units_wasted:     int
    sold_out:         bool  = False
    temperature_max:  Optional[float] = None
    precipitation_mm: Optional[float] = None
    is_holiday:       bool  = False
    is_local_event:   bool  = False
    event_notes:      Optional[str] = None
    notes:            Optional[str] = None

    @model_validator(mode="after")
    def check_units_consistency(self):
        total = self.units_sold + self.units_wasted
        if total > self.units_produced:
            raise ValueError(
                "units_sold + units_wasted cannot exceed units_produced"
            )
        return self


@router.post("/", status_code=201)
def create_log(
    payload: DailyLogEntry,
    db: sqlite3.Connection = Depends(get_db),
):
    try:
        db.execute("""
            INSERT INTO daily_log (
                date, product_id, units_produced, units_sold, units_wasted,
                sold_out, temperature_max, precipitation_mm,
                is_holiday, is_local_event, event_notes, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            payload.date.isoformat(),
            payload.product_id,
            payload.units_produced,
            payload.units_sold,
            payload.units_wasted,
            payload.sold_out,
            payload.temperature_max,
            payload.precipitation_mm,
            payload.is_holiday,
            payload.is_local_event,
            payload.event_notes,
            payload.notes,
        ))
        db.commit()
        return {"message": "Log entry saved."}
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="A log entry for this product and date already exists."
        )


@router.get("/")
def get_logs(
    date_from:  Optional[date] = Query(default=None),
    date_to:    Optional[date] = Query(default=None),
    product_id: Optional[int]  = Query(default=None),
    db: sqlite3.Connection = Depends(get_db),
):
    query  = "SELECT * FROM daily_log WHERE 1=1"
    params = []

    if date_from:
        query += " AND date >= ?"
        params.append(date_from.isoformat())
    if date_to:
        query += " AND date <= ?"
        params.append(date_to.isoformat())
    if product_id:
        query += " AND product_id = ?"
        params.append(product_id)

    query += " ORDER BY date DESC"
    rows = db.execute(query, params).fetchall()
    return [dict(row) for row in rows]