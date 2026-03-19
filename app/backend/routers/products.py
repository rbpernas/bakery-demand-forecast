"""
products.py
-----------
CRUD endpoints for the products catalog.
"""

import sqlite3
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.backend.database import get_db

router = APIRouter()


class ProductCreate(BaseModel):
    name:      str
    category:  str
    unit_cost: Optional[float] = None


class ProductUpdate(BaseModel):
    name:      Optional[str]   = None
    unit_cost: Optional[float] = None


@router.get("/")
def list_products(db: sqlite3.Connection = Depends(get_db)):
    rows = db.execute(
        "SELECT * FROM products WHERE is_active = 1 ORDER BY category, name"
    ).fetchall()
    return [dict(row) for row in rows]


@router.post("/", status_code=201)
def create_product(
    payload: ProductCreate,
    db: sqlite3.Connection = Depends(get_db),
):
    valid_categories = ("bread", "pastry", "coca")
    if payload.category not in valid_categories:
        raise HTTPException(
            status_code=400,
            detail=f"Category must be one of {valid_categories}",
        )
    try:
        cursor = db.execute(
            "INSERT INTO products (name, category, unit_cost) VALUES (?, ?, ?)",
            (payload.name, payload.category, payload.unit_cost),
        )
        db.commit()
        return {"product_id": cursor.lastrowid, **payload.model_dump()}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="Product name already exists.")


@router.patch("/{product_id}")
def update_product(
    product_id: int,
    payload:    ProductUpdate,
    db:         sqlite3.Connection = Depends(get_db),
):
    product = db.execute(
        "SELECT * FROM products WHERE product_id = ? AND is_active = 1",
        (product_id,)
    ).fetchone()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")

    if payload.name is not None:
        db.execute(
            "UPDATE products SET name = ? WHERE product_id = ?",
            (payload.name, product_id)
        )
    if payload.unit_cost is not None:
        db.execute(
            "UPDATE products SET unit_cost = ? WHERE product_id = ?",
            (payload.unit_cost, product_id)
        )
    db.commit()
    return {"message": "Product updated."}


@router.delete("/{product_id}")
def deactivate_product(
    product_id: int,
    db: sqlite3.Connection = Depends(get_db),
):
    product = db.execute(
        "SELECT * FROM products WHERE product_id = ? AND is_active = 1",
        (product_id,)
    ).fetchone()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")

    db.execute(
        "UPDATE products SET is_active = 0 WHERE product_id = ?",
        (product_id,)
    )
    db.commit()
    return {"message": "Product deactivated. Historical data preserved."}