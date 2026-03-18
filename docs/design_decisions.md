# Design Decisions

This document explains the reasoning behind major technical choices in this project.

## Database: SQLite over PostgreSQL (MVP)

SQLite was chosen for the initial version because the bakery operates as a single-user system on a single machine, and SQLite requires zero server setup. Migration to PostgreSQL is straightforward with SQLAlchemy if the system ever needs to scale.

## Hybrid model: rules first, ML second

Starting with zero historical data makes supervised ML impossible from day one. The rule-based model provides immediate value while passively collecting the data needed to train a proper ML model. The threshold to switch is estimated at ~60 days of logs per product.

## `sold_out` field

When a product sells out, the recorded `units_sold` is not the true demand — it's a lower bound. This is a classic case of *censored data*. Tracking `sold_out` explicitly allows the model to treat these observations differently (e.g., with Tobit regression or by adding a buffer multiplier in the rule-based phase).

## `is_active` instead of DELETE for products

Deleting a product would orphan its historical records in `daily_log`. Soft-deletion via `is_active` preserves the full history, which is important for model training.

## Product categories: bread / pastry / coca

These three categories reflect meaningfully different demand patterns:
- **Bread**: daily staple, high volume, predictable weekday/weekend pattern
- **Pastry**: more discretionary, weather and mood dependent
- **Coca**: highly seasonal and event-driven (local festivals, holidays)

Keeping them as a constrained CHECK in the DB prevents data quality issues.
