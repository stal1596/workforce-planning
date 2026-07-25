import os
import random
from datetime import date, timedelta

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()
engine = create_engine(os.environ["DATABASE_URL"])

DAYS_OF_HISTORY = 90

# product_id: (base_daily_qty, {weekday: multiplier})  weekday 0=Mon..6=Sun
PATTERNS = {
    1: (6, {3: 2.2}),           # Milk 1L — spikes Thursday, per ch1
    2: (3, {4: 1.5, 5: 1.5}),   # Yoghurt 500g — busier Fri/Sat
    3: (5, {}),                 # Bread Loaf — fairly flat
}


def generate(product_id, base, multipliers, start, end):
    rows, day = [], start
    while day <= end:
        mult = multipliers.get(day.weekday(), 1.0)
        qty = max(0, round(random.gauss(base * mult, base * 0.25)))
        if qty > 0:
            rows.append({"product_id": product_id, "qty": qty, "sold_at": day})
        day += timedelta(days=1)
    return rows


def main():
    end = date.today() - timedelta(days=1)
    start = end - timedelta(days=DAYS_OF_HISTORY - 1)
    rows = [r for pid, (b, m) in PATTERNS.items() for r in generate(pid, b, m, start, end)]

    with engine.begin() as conn:
        for row in rows:
            conn.execute(
                text("INSERT INTO sales (product_id, qty, sold_at) VALUES (:product_id, :qty, :sold_at)"),
                row,
            )
    print(f"Inserted {len(rows)} synthetic sales rows over {DAYS_OF_HISTORY} days.")


if __name__ == "__main__":
    main()