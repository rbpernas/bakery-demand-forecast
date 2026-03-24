"""
init_db.py
----------
Initializes the SQLite database and creates all tables.
Run once when setting up the project for the first time.

Usage:
    python src/data/init_db.py
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "../../data/raw/bakery.db")


def get_connection() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)


def create_tables(conn: sqlite3.Connection) -> None:
    cursor = conn.cursor()

    # --- Products catalog ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            product_id  INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL UNIQUE,
            category    TEXT    NOT NULL CHECK(category IN ('bread', 'pastry', 'coca')),
            unit_cost   REAL,
            is_active   BOOLEAN NOT NULL DEFAULT 1,
            created_at  DATE    NOT NULL DEFAULT (DATE('now'))
        )
    """)

    # --- Daily production and sales log ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_log (
            log_id           INTEGER PRIMARY KEY AUTOINCREMENT,
            date             DATE    NOT NULL,
            product_id       INTEGER NOT NULL REFERENCES products(product_id),
            units_produced   INTEGER NOT NULL CHECK(units_produced >= 0),
            units_sold       INTEGER NOT NULL CHECK(units_sold >= 0),
            units_wasted     INTEGER NOT NULL CHECK(units_wasted >= 0),
            sold_out         BOOLEAN NOT NULL DEFAULT 0,
            temperature_max  REAL,
            precipitation_mm REAL,
            is_holiday       BOOLEAN NOT NULL DEFAULT 0,
            is_local_event   BOOLEAN NOT NULL DEFAULT 0,
            event_notes      TEXT,
            notes            TEXT,
            UNIQUE(date, product_id)
        )
    """)

    conn.commit()
    print("✅ Tables created successfully.")


def seed_initial_products(conn: sqlite3.Connection) -> None:
    """
    Insert a starter set of products. 
    The bakery owner can add more from the web app later.
    """
    initial_products = [
        ("barra",     "bread",  0.30),
        ("hogaza",    "bread",  1.20),
        ("croissant", "pastry", 0.45),
        ("napolitana","pastry", 0.50),
        ("coca",      "coca",   1.80),
    ]

    cursor = conn.cursor()
    cursor.executemany("""
        INSERT OR IGNORE INTO products (name, category, unit_cost)
        VALUES (?, ?, ?)
    """, initial_products)
    conn.commit()

    inserted = cursor.rowcount
    print(f"✅ Seeded {inserted} initial product(s).")
def create_orders_tables(conn: sqlite3.Connection) -> None:
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id  INTEGER PRIMARY KEY AUTOINCREMENT,
            name         TEXT    NOT NULL,
            phone        TEXT,
            created_at   DATE    NOT NULL DEFAULT (DATE('now'))
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id      INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id   INTEGER NOT NULL REFERENCES customers(customer_id),
            product_id    INTEGER NOT NULL REFERENCES products(product_id),
            quantity      INTEGER NOT NULL CHECK(quantity > 0),
            order_type    TEXT    NOT NULL CHECK(order_type IN ('once', 'daily', 'weekdays', 'weekends')),
            start_date    DATE    NOT NULL,
            end_date      DATE,
            is_active     BOOLEAN NOT NULL DEFAULT 1,
            notes         TEXT,
            created_at    DATE    NOT NULL DEFAULT (DATE('now'))
        )
    """)

    conn.commit()
    print("✅ Orders tables created.")

def main() -> None:
    print(f"Initializing database at: {os.path.abspath(DB_PATH)}")
    conn = get_connection()
    try:
        create_tables(conn)
        seed_initial_products(conn)
        create_orders_tables(conn)
        print("\n🎉 Database ready.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
