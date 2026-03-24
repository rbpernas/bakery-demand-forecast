"""
stats.py
--------
Endpoints for aggregated statistics used in the trends dashboard.

GET /stats/summary     — totals per product (last N days)
GET /stats/daily       — daily waste and sales (last N days)
"""

import sqlite3
from datetime import date, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.backend.database import get_db

router = APIRouter()


@router.get("/summary")
def get_summary(
    days: int = Query(default=30),
    db: sqlite3.Connection = Depends(get_db),
):
    """
    Returns totals per product for the last N days.
    """
    since = (date.today() - timedelta(days=days)).isoformat()

    rows = db.execute("""
        SELECT
            p.name                          AS product,
            p.category                      AS category,
            SUM(dl.units_produced)          AS total_produced,
            SUM(dl.units_sold)              AS total_sold,
            SUM(dl.units_wasted)            AS total_wasted,
            ROUND(100.0 * SUM(dl.units_wasted) /
                NULLIF(SUM(dl.units_produced), 0), 1) AS waste_pct,
            SUM(CASE WHEN dl.sold_out THEN 1 ELSE 0 END) AS days_sold_out,
            COUNT(*)                        AS days_recorded
        FROM daily_log dl
        JOIN products p ON dl.product_id = p.product_id
        WHERE dl.date >= ?
        GROUP BY p.product_id
        ORDER BY p.category, p.name
    """, (since,)).fetchall()

    return [dict(row) for row in rows]


@router.get("/daily")
def get_daily(
    days: int = Query(default=30),
    db: sqlite3.Connection = Depends(get_db),
):
    """
    Returns daily aggregated waste and sales for the last N days.
    """
    since = (date.today() - timedelta(days=days)).isoformat()

    rows = db.execute("""
        SELECT
            dl.date                         AS date,
            SUM(dl.units_produced)          AS total_produced,
            SUM(dl.units_sold)              AS total_sold,
            SUM(dl.units_wasted)            AS total_wasted
        FROM daily_log dl
        WHERE dl.date >= ?
        GROUP BY dl.date
        ORDER BY dl.date ASC
    """, (since,)).fetchall()

    return [dict(row) for row in rows]