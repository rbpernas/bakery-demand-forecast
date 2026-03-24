"""
seed_sample_data.py
-------------------
Populates the database with 30 days of realistic fake data.
Only for development and demo purposes.

Usage:
    python src/data/seed_sample_data.py
"""

import sqlite3
import random
from datetime import date, timedelta
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "../../data/raw/bakery.db")

BASE = {
    1: 60,
    2: 15,
    3: 20,
    4: 20,
    5: 5,
}

DOW_MULT = {0: 0.9, 1: 0.85, 2: 0.9, 3: 0.9, 4: 1.1, 5: 1.6, 6: 1.4}


def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    today = date.today()
    start = today - timedelta(days=30)

    for i in range(30):
        day = start + timedelta(days=i)
        dow = day.weekday()
        mult = DOW_MULT[dow]
        temp = round(random.uniform(10, 25), 1)
        precip = round(random.choice([0, 0, 0, 2, 8, 15]), 1)

        for product_id, base in BASE.items():
            produced = max(1, round(base * mult * random.uniform(0.9, 1.1)))
            sell_rate = random.uniform(0.80, 1.0)
            sold = min(produced, round(produced * sell_rate))
            wasted = produced - sold
            sold_out = sold == produced

            try:
                cursor.execute("""
                    INSERT INTO daily_log (
                        date, product_id, units_produced, units_sold,
                        units_wasted, sold_out, temperature_max,
                        precipitation_mm, is_holiday, is_local_event
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, 0)
                """, (
                    day.isoformat(), product_id, produced,
                    sold, wasted, sold_out, temp, precip
                ))
            except sqlite3.IntegrityError:
                pass

    conn.commit()
    conn.close()
    print("✅ 30 days of sample data inserted.")


if __name__ == "__main__":
    main()