"""
constants.py
------------
Central configuration for the rule-based model.
All multipliers and thresholds are defined here so they can be
adjusted without touching the prediction logic.
"""

# -------------------------------------------------------------------
# Village context
# -------------------------------------------------------------------
PERMANENT_RESIDENTS = 500

# Estimated % of residents that buy bread on a given weekday
BASE_PURCHASE_RATE = 0.30  # 1 in 3 residents buys something every weekday

# -------------------------------------------------------------------
# Base daily demand (units) per product — starting estimates
# These will be refined by the model as real data comes in
# -------------------------------------------------------------------
BASE_DEMAND = {
    "barra":      60,
    "hogaza":     15,
    "croissant":  20,
    "napolitana": 20,
    "coca":        5,
}

# -------------------------------------------------------------------
# Day-of-week multipliers (0 = Monday, 6 = Sunday)
# -------------------------------------------------------------------
DOW_MULTIPLIERS = {
    0: 0.90,  # Monday    — slow start
    1: 0.85,  # Tuesday   — quietest day
    2: 0.90,  # Wednesday
    3: 0.90,  # Thursday
    4: 1.10,  # Friday    — pre-weekend boost
    5: 1.60,  # Saturday  — peak day, visitors arrive
    6: 1.40,  # Sunday    — still busy, closes earlier
}

# -------------------------------------------------------------------
# Special context multipliers (applied on top of DOW)
# -------------------------------------------------------------------
HOLIDAY_MULTIPLIER     = 1.50  # National or regional holiday
LOCAL_EVENT_MULTIPLIER = 1.80  # Village fair, market, festival

# -------------------------------------------------------------------
# Weather multipliers
# -------------------------------------------------------------------
# Cold weather → more bread bought
COLD_TEMP_THRESHOLD  = 10.0   # °C
COLD_TEMP_MULTIPLIER = 1.10

# Heavy rain → fewer visitors, less demand
RAIN_THRESHOLD_MM    = 10.0   # mm
RAIN_MULTIPLIER      = 0.85

# -------------------------------------------------------------------
# Category-level adjustments
# Cocas are much more event-driven than bread
# -------------------------------------------------------------------
CATEGORY_EVENT_BOOST = {
    "bread":  1.0,
    "pastry": 1.2,
    "coca":   2.5,  # Cocas spike hard on local events
}

# -------------------------------------------------------------------
# ML readiness threshold
# Minimum number of observations before switching a product to ML
# -------------------------------------------------------------------
MIN_OBSERVATIONS_FOR_ML = 60
