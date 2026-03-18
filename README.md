# 🥖 Bakery Demand Forecast

A demand prediction system for a small-town bakery, built to minimize waste while ensuring daily product availability.

## The Problem

Small bakeries face a daily challenge: produce too little and disappoint customers, produce too much and waste product and margin. This system helps a bakery owner answer every morning: *"How much should I bake today?"*

The challenge is compounded by a **cold start problem** — the bakery opens with zero historical data. This project tackles that with a hybrid approach: a rule-based model that works from day one, gradually replaced by a machine learning model as data accumulates.

## Project Phases

| Phase | Description | Status |
|---|---|---|
| 0 | Data schema & collection design | ✅ Done |
| 1 | Rule-based prediction model | 🔄 In progress |
| 2 | ML model (LightGBM / Prophet) | ⏳ Pending data |
| 3 | Web application | ⏳ Pending |
| 4 | Continuous refinement | ⏳ Ongoing |

## Tech Stack

- **Backend**: Python, FastAPI, SQLAlchemy
- **Database**: SQLite (MVP) 
- **ML**: scikit-learn, LightGBM, Prophet
- **Frontend**: React

## Setup

```bash
# Clone the repository
git clone https://github.com/your-username/bakery-demand-forecast.git
cd bakery-demand-forecast

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize the database
python src/data/init_db.py
```

## Project Structure

```
bakery-demand-forecast/
├── data/
│   ├── raw/            # Daily logs as collected
│   ├── processed/      # Clean data with engineered features
│   └── external/       # Public holidays, weather data
├── notebooks/
│   ├── 01_eda.ipynb
│   └── 02_model_exploration.ipynb
├── src/
│   ├── data/           # Ingestion and cleaning scripts
│   ├── features/       # Feature engineering
│   ├── models/         # Rule-based and ML models
│   └── utils/          # Helpers and constants
├── app/
│   ├── backend/        # FastAPI application
│   └── frontend/       # Web interface
├── tests/
└── docs/               # Design decisions and diagrams
```

## Key Design Decisions

See [`docs/design_decisions.md`](docs/design_decisions.md) for the reasoning behind major technical choices.

## Context

Built as a real-world portfolio project. The bakery serves a small village (~500 permanent residents, more on weekends and holidays) in rural Spain.
