"""
test_rule_based.py
------------------
Unit tests for the rule-based prediction model.

Run with:
    pytest tests/test_rule_based.py -v
"""

import sqlite3
import tempfile
import os
from datetime import date

import pytest

from src.models.rule_based import RuleBasedModel
from src.data.init_db import create_tables, seed_initial_products


# -------------------------------------------------------------------
# Fixtures
# -------------------------------------------------------------------

@pytest.fixture
def db_path():
    """Creates a temporary in-memory-like DB for each test."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        path = f.name
    conn = sqlite3.connect(path)
    create_tables(conn)
    seed_initial_products(conn)
    conn.close()
    yield path
    os.unlink(path)


@pytest.fixture
def model(db_path):
    return RuleBasedModel(db_path=db_path)


# -------------------------------------------------------------------
# Tests
# -------------------------------------------------------------------

class TestPredictSingleProduct:

    def test_returns_positive_units(self, model):
        pred = model.predict(
            product_name="barra",
            category="bread",
            target_date=date(2024, 6, 17),  # Monday
        )
        assert pred.units > 0

    def test_weekend_higher_than_weekday(self, model):
        monday = model.predict(
            product_name="barra",
            category="bread",
            target_date=date(2024, 6, 17),  # Monday
        )
        saturday = model.predict(
            product_name="barra",
            category="bread",
            target_date=date(2024, 6, 22),  # Saturday
        )
        assert saturday.units > monday.units

    def test_holiday_increases_demand(self, model):
        normal = model.predict(
            product_name="barra",
            category="bread",
            target_date=date(2024, 6, 17),
            is_holiday=False,
        )
        holiday = model.predict(
            product_name="barra",
            category="bread",
            target_date=date(2024, 6, 17),
            is_holiday=True,
        )
        assert holiday.units > normal.units

    def test_local_event_boosts_coca_more_than_bread(self, model):
        bread_normal = model.predict("barra",  "bread", date(2024, 6, 17))
        bread_event  = model.predict("barra",  "bread", date(2024, 6, 17), is_local_event=True)
        coca_normal  = model.predict("coca",   "coca",  date(2024, 6, 17))
        coca_event   = model.predict("coca",   "coca",  date(2024, 6, 17), is_local_event=True)

        bread_ratio = bread_event.units / bread_normal.units
        coca_ratio  = coca_event.units  / coca_normal.units

        assert coca_ratio > bread_ratio

    def test_rain_reduces_demand(self, model):
        dry = model.predict(
            product_name="barra",
            category="bread",
            target_date=date(2024, 6, 17),
            precipitation_mm=0.0,
        )
        rainy = model.predict(
            product_name="barra",
            category="bread",
            target_date=date(2024, 6, 17),
            precipitation_mm=15.0,
        )
        assert rainy.units < dry.units

    def test_cold_increases_demand(self, model):
        warm = model.predict(
            product_name="barra",
            category="bread",
            target_date=date(2024, 6, 17),
            temperature_max=25.0,
        )
        cold = model.predict(
            product_name="barra",
            category="bread",
            target_date=date(2024, 6, 17),
            temperature_max=5.0,
        )
        assert cold.units > warm.units

    def test_confidence_low_with_no_data(self, model):
        pred = model.predict(
            product_name="barra",
            category="bread",
            target_date=date(2024, 6, 17),
        )
        assert pred.confidence == "low"

    def test_breakdown_contains_expected_keys(self, model):
        pred = model.predict("barra", "bread", date(2024, 6, 17))
        for key in ("base", "day_of_week", "holiday", "local_event", "weather"):
            assert key in pred.breakdown


class TestPredictAll:

    def test_returns_prediction_for_each_active_product(self, model):
        predictions = model.predict_all(target_date=date(2024, 6, 17))
        assert len(predictions) == 5  # matches seed_initial_products

    def test_all_predictions_have_positive_units(self, model):
        predictions = model.predict_all(target_date=date(2024, 6, 17))
        assert all(p.units > 0 for p in predictions)
