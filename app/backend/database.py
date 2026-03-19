"""
database.py
-----------
Database connection helper for FastAPI dependency injection.
"""

import os
import sqlite3
from typing import Generator

DB_PATH = os.path.join(
    os.path.dirname(__file__), "../../data/raw/bakery.db"
)


def get_db() -> Generator:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
    finally:
        conn.close()