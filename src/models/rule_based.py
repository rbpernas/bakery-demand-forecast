"""
rule_based.py
-------------
Rule-based demand prediction model for the bakery.

Works from day one with zero historical data, using a set of
calibrated multipliers. As real data accumulates, the base demand
estimates are automatically adjusted using observed averages.

Usage:
    from src.models.rule_based import RuleBasedModel

    model = RuleBasedModel()
    prediction = model.predict(
        product_name="barra",
        date=date(2024, 6, 15),
        is_holiday=False,
        is_local_event=False,
        temperature_max=22.0,
        precipitation_mm=0.0,
    )
    print(prediction)  # {'units': 65, 'confidence': 'low'}
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import date
from typing import Optional

from src.utils.constants import (
    BASE_DEMAND,
    CATEGORY_EVENT_BOOST,
    COLD_TEMP_MULTIPLIER,
    COLD_TEMP_THRESHOLD,
    DOW_MULTIPLIERS,
    HOLIDAY_MULTIPLIER,
    LOCAL_EVENT_MULTIPLIER,
    MIN_OBSERVATIONS_FOR_ML,
    RAIN_MULTIPLIER,
    RAIN_THRESHOLD_MM,
)


# -------------------------------------------------------------------
# Data classes
# -------------------------------------------------------------------

@dataclass
class Prediction:
    product_name: str
    category:     str
    target_date:  date
    units:        int
    confidence:   str
    observations: int
    breakdown:    dict
# -------------------------------------------------------------------
# Model
# -------------------------------------------------------------------

class RuleBasedModel:
    """
    Demand predictor based on calibrated multipliers.

    Automatically adjusts base demand using historical averages
    once enough observations are available per product.
    """

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path

    # ----------------------------------------------------------------
    # Public API
    # ----------------------------------------------------------------

    def predict(
        self,
        product_name:     str,
        category:         str,
        target_date:      date,
        is_holiday:       bool = False,
        is_local_event:   bool = False,
        temperature_max:  Optional[float] = None,
        precipitation_mm: Optional[float] = None,
    ) -> Prediction:
        """
        Returns a demand prediction for one product on one day.
        """
        # 1. Get base demand (static or learned from history)
        base, observations = self._get_base_demand(product_name)

        # 2. Apply multipliers
        breakdown = {"base": base}

        dow = DOW_MULTIPLIERS[target_date.weekday()]
        breakdown["day_of_week"] = dow

        holiday = HOLIDAY_MULTIPLIER if is_holiday else 1.0
        breakdown["holiday"] = holiday

        if is_local_event:
            event = LOCAL_EVENT_MULTIPLIER * CATEGORY_EVENT_BOOST.get(category, 1.0)
        else:
            event = 1.0
        breakdown["local_event"] = event

        weather = self._weather_multiplier(temperature_max, precipitation_mm)
        breakdown["weather"] = weather

        # 3. Compute final prediction
        raw = base * dow * holiday * event * weather
        units = max(1, round(raw))

        # 4. Assign confidence based on observations
        confidence = self._confidence_level(observations)

        return Prediction(
            product_name=product_name,
            category=category,
            target_date=target_date,
            units=units,
            confidence=confidence,
            observations=observations,
            breakdown=breakdown,
        )

    def predict_all(
        self,
        target_date:      date,
        is_holiday:       bool = False,
        is_local_event:   bool = False,
        temperature_max:  Optional[float] = None,
        precipitation_mm: Optional[float] = None,
    ) -> list[Prediction]:
        """
        Returns predictions for all active products.
        """
        products = self._get_active_products()
        return [
            self.predict(
                product_name=row["name"],
                category=row["category"],
                target_date=target_date,
                is_holiday=is_holiday,
                is_local_event=is_local_event,
                temperature_max=temperature_max,
                precipitation_mm=precipitation_mm,
            )
            for row in products
        ]

    # ----------------------------------------------------------------
    # Private helpers
    # ----------------------------------------------------------------

    def _get_base_demand(self, product_name: str) -> tuple[float, int]:
        """
        Returns (base_demand, n_observations).

        If enough data exists, uses the empirical average of
        weekday-normalised sales. Otherwise falls back to constants.
        """
        query = """
            SELECT
                AVG(units_sold) as avg_sold,
                COUNT(*)        as n_obs
            FROM daily_log dl
            JOIN products p ON dl.product_id = p.product_id
            WHERE p.name = ?
              AND dl.sold_out = 0          -- exclude censored days
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(query, (product_name,)).fetchone()

        n_obs = row["n_obs"] if row else 0
        avg   = row["avg_sold"] if row and row["avg_sold"] else None

        # If we have enough non-censored observations, blend empirical
        # average with the constant (weighted blend, not hard switch)
        if n_obs >= 10 and avg is not None:
            weight  = min(n_obs / MIN_OBSERVATIONS_FOR_ML, 1.0)
            static  = BASE_DEMAND.get(product_name, 10)
            base    = weight * avg + (1 - weight) * static
        else:
            base = BASE_DEMAND.get(product_name, 10)

        return base, n_obs

    def _weather_multiplier(
        self,
        temperature_max:  Optional[float],
        precipitation_mm: Optional[float],
    ) -> float:
        multiplier = 1.0
        if temperature_max is not None and temperature_max < COLD_TEMP_THRESHOLD:
            multiplier *= COLD_TEMP_MULTIPLIER
        if precipitation_mm is not None and precipitation_mm > RAIN_THRESHOLD_MM:
            multiplier *= RAIN_MULTIPLIER
        return multiplier

    def _confidence_level(self, observations: int) -> str:
        if observations < 14:
            return "low"
        elif observations < MIN_OBSERVATIONS_FOR_ML:
            return "medium"
        else:
            return "high"

    def _get_active_products(self) -> list[sqlite3.Row]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            return conn.execute(
                "SELECT name, category FROM products WHERE is_active = 1"
            ).fetchall()
