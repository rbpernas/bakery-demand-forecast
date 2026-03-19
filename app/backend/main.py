"""
main.py
-------
FastAPI application entry point.

Run with:
    uvicorn app.backend.main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.backend.routers import predictions, products, logs

app = FastAPI(
    title="Bakery Demand Forecast API",
    description="Demand prediction system for a small-town bakery.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(predictions.router, prefix="/predictions", tags=["Predictions"])
app.include_router(products.router,    prefix="/products",    tags=["Products"])
app.include_router(logs.router,        prefix="/logs",        tags=["Logs"])


@app.get("/health")
def health_check():
    return {"status": "ok"}