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

@router.get("/dates/")
def get_logged_dates(db: sqlite3.Connection = Depends(get_db)):
    """
    Returns all dates that have at least one log entry.
    Used by the calendar to mark days with data.
    """
    rows = db.execute(
        "SELECT DISTINCT date FROM daily_log ORDER BY date ASC"
    ).fetchall()
    return [row["date"] for row in rows]


@router.get("/day/")
def get_day_detail(
    date: str = Query(...),
    db: sqlite3.Connection = Depends(get_db),
):
    """
    Returns full detail for a specific day:
    sales per product, weather, notes and orders.
    """
    logs = db.execute("""
        SELECT
            p.name          AS product,
            p.category      AS category,
            dl.units_produced,
            dl.units_sold,
            dl.units_wasted,
            dl.sold_out,
            dl.notes,
            dl.temperature_max,
            dl.precipitation_mm,
            dl.is_holiday,
            dl.is_local_event,
            dl.event_notes
        FROM daily_log dl
        JOIN products p ON dl.product_id = p.product_id
        WHERE dl.date = ?
        ORDER BY p.category, p.name
    """, (date,)).fetchall()

    if not logs:
        return {"date": date, "logs": [], "orders": []}

    # Get orders for this day
    all_orders = db.execute("""
        SELECT o.*, c.name AS customer_name, c.phone AS customer_phone, p.name AS product_name
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        JOIN products p ON o.product_id = p.product_id
        WHERE o.is_active = 1
    """).fetchall()

    from datetime import date as date_type
    target = date_type.fromisoformat(date)

    from app.backend.routers.orders import order_applies_on
    applicable_orders = [
        dict(row) for row in all_orders
        if order_applies_on(dict(row), target)
    ]

    first = dict(logs[0])
    return {
        "date":             date,
        "temperature_max":  first["temperature_max"],
        "precipitation_mm": first["precipitation_mm"],
        "is_holiday":       first["is_holiday"],
        "is_local_event":   first["is_local_event"],
        "event_notes":      first["event_notes"],
        "notes":            first["notes"],
        "logs":             [dict(row) for row in logs],
        "orders":           applicable_orders,
    }