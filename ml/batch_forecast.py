import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

from serve import load_model, predict  # same function Step 5 exposes over HTTP — no separate logic to drift

load_dotenv()
engine = create_engine(os.environ["DATABASE_URL"])
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")


def main():
    load_model()
    with open(os.path.join(MODEL_DIR, "production.txt")) as f:
        version = f.read().strip()

    with engine.begin() as conn:
        conn.execute(text("DELETE FROM forecasts"))
        product_ids = [r[0] for r in conn.execute(text("SELECT id FROM products"))]
        written = 0
        for pid in product_ids:
            try:
                result = predict(pid)
            except Exception:
                continue
            for day in result["forecast"]:
                conn.execute(
                    text("INSERT INTO forecasts (product_id, date, predicted_qty, model_version) "
                         "VALUES (:pid, :date, :qty, :version)"),
                    {"pid": pid, "date": day["date"], "qty": day["predicted_qty"], "version": version},
                )
                written += 1
    print(f"Wrote {written} forecast rows using {version}.")


if __name__ == "__main__":
    main()