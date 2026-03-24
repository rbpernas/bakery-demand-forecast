"""
orders.py
---------
Endpoints for managing customer orders and reservations.

GET    /orders/                    — list all active orders
GET    /orders/day?date=...        — orders for a specific day
POST   /orders/customers/          — create a customer
GET    /orders/customers/          — list all customers
POST   /orders/                    — create an order
DELETE /orders/{order_id}          — cancel an order
"""

import sqlite3
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from app.backend.database import get_db

router = APIRouter()


# -------------------------------------------------------------------
# Schemas
# -------------------------------------------------------------------

class CustomerCreate(BaseModel):
    name:  str
    phone: Optional[str] = None


class OrderCreate(BaseModel):
    customer_id: int
    product_id:  int
    quantity:    int
    order_type:  str  # once | daily | weekdays | weekends
    start_date:  date
    end_date:    Optional[date] = None
    notes:       Optional[str] = None


# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------

def order_applies_on(order: dict, target: date) -> bool:
    """Returns True if an order should be fulfilled on the target date."""
    start = date.fromisoformat(order["start_date"])
    end   = date.fromisoformat(order["end_date"]) if order["end_date"] else None

    if target < start:
        return False
    if end and target > end:
        return False

    order_type = order["order_type"]
    if order_type == "once":
        return target == start
    elif order_type == "daily":
        return True
    elif order_type == "weekdays":
        return target.weekday() < 5
    elif order_type == "weekends":
        return target.weekday() >= 5
    return False


# -------------------------------------------------------------------
# Customers
# -------------------------------------------------------------------

@router.get("/customers/")
def list_customers(db: sqlite3.Connection = Depends(get_db)):
    rows = db.execute(
        "SELECT * FROM customers ORDER BY name"
    ).fetchall()
    return [dict(row) for row in rows]


@router.post("/customers/", status_code=201)
def create_customer(
    payload: CustomerCreate,
    db: sqlite3.Connection = Depends(get_db),
):
    if not payload.name.strip():
        raise HTTPException(status_code=400, detail="Name is required.")
    cursor = db.execute(
        "INSERT INTO customers (name, phone) VALUES (?, ?)",
        (payload.name.strip(), payload.phone),
    )
    db.commit()
    return {"customer_id": cursor.lastrowid, "name": payload.name, "phone": payload.phone}


# -------------------------------------------------------------------
# Orders
# -------------------------------------------------------------------

@router.get("/")
def list_orders(db: sqlite3.Connection = Depends(get_db)):
    rows = db.execute("""
        SELECT
            o.*,
            c.name  AS customer_name,
            c.phone AS customer_phone,
            p.name  AS product_name
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        JOIN products  p ON o.product_id  = p.product_id
        WHERE o.is_active = 1
        ORDER BY o.start_date DESC
    """).fetchall()
    return [dict(row) for row in rows]


@router.get("/day/")
def get_orders_for_day(
    target_date: date = Query(default_factory=date.today),
    db: sqlite3.Connection = Depends(get_db),
):
    """
    Returns all active orders that apply on a given date,
    along with the total units reserved per product.
    """
    all_orders = db.execute("""
        SELECT
            o.*,
            c.name  AS customer_name,
            c.phone AS customer_phone,
            p.name  AS product_name
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        JOIN products  p ON o.product_id  = p.product_id
        WHERE o.is_active = 1
    """).fetchall()

    applicable = [
        dict(row) for row in all_orders
        if order_applies_on(dict(row), target_date)
    ]

    # Aggregate by product
    totals = {}
    for order in applicable:
        pid = order["product_id"]
        if pid not in totals:
            totals[pid] = {"product_id": pid, "product_name": order["product_name"], "total_reserved": 0}
        totals[pid]["total_reserved"] += order["quantity"]

    return {
        "date":    target_date.isoformat(),
        "orders":  applicable,
        "totals":  list(totals.values()),
    }


@router.post("/", status_code=201)
def create_order(
    payload: OrderCreate,
    db: sqlite3.Connection = Depends(get_db),
):
    valid_types = ("once", "daily", "weekdays", "weekends")
    if payload.order_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"order_type must be one of {valid_types}"
        )
    if payload.end_date and payload.end_date < payload.start_date:
        raise HTTPException(
            status_code=400,
            detail="end_date cannot be before start_date"
        )

    # Check customer and product exist
    customer = db.execute(
        "SELECT customer_id FROM customers WHERE customer_id = ?",
        (payload.customer_id,)
    ).fetchone()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found.")

    product = db.execute(
        "SELECT product_id FROM products WHERE product_id = ? AND is_active = 1",
        (payload.product_id,)
    ).fetchone()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")

    cursor = db.execute("""
        INSERT INTO orders (customer_id, product_id, quantity, order_type, start_date, end_date, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        payload.customer_id,
        payload.product_id,
        payload.quantity,
        payload.order_type,
        payload.start_date.isoformat(),
        payload.end_date.isoformat() if payload.end_date else None,
        payload.notes,
    ))
    db.commit()
    return {"order_id": cursor.lastrowid, **payload.model_dump()}


@router.delete("/{order_id}")
def cancel_order(
    order_id: int,
    db: sqlite3.Connection = Depends(get_db),
):
    order = db.execute(
        "SELECT * FROM orders WHERE order_id = ? AND is_active = 1",
        (order_id,)
    ).fetchone()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found.")

    db.execute(
        "UPDATE orders SET is_active = 0 WHERE order_id = ?",
        (order_id,)
    )
    db.commit()
    return {"message": "Order cancelled."}