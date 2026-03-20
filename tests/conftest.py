"""
conftest.py
-----------
Shared fixtures for all API tests.

pytest loads this file automatically before running any test.
The fixtures here set up a clean temporary database and a test
client that talks to our FastAPI app without needing a real server.
"""

import os
import sqlite3
import tempfile

import pytest
from fastapi.testclient import TestClient

from src.data.init_db import create_tables, seed_initial_products


@pytest.fixture(scope="function")
def db_path():
    """
    Creates a fresh temporary SQLite database for each test function.
    Deleted automatically when the test finishes.
    """
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        path = f.name

    conn = sqlite3.connect(path)
    create_tables(conn)
    seed_initial_products(conn)
    conn.close()

    yield path

    try:
        os.unlink(path)
    except PermissionError:
        pass


@pytest.fixture(scope="function")
def client(db_path):
    """
    Returns a FastAPI TestClient wired to a temporary database.
    Each test gets its own clean client + database.
    """
    # Override the DB_PATH used by the app before importing the app
    import app.backend.database as db_module
    db_module.DB_PATH = db_path

    # Also override the DB_PATH used by the rule-based model inside the router
    import app.backend.routers.predictions as pred_module
    pred_module.DB_PATH = db_path

    from app.backend.main import app
    return TestClient(app)