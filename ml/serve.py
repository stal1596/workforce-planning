import os
from datetime import date, timedelta

import joblib
import pandas as pd
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine

from features import FEATURE_COLUMNS, build_features, fill_daily_gaps

load_dotenv()
engine = create_engine(os.environ["DATABASE_URL"])
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")

app = FastAPI(title="GreenBasket ML Service")
_bundle: dict = {}


@app.on_event("startup")
def load_model():
    global _bundle
    with open(os.path.join(MODEL_DIR, "production.txt")) as f:
        filename = f.read().strip()
    _bundle = joblib.load(os.path.join(MODEL_DIR, filename))
    print(f"Loaded {filename}: {len(_bundle)} product models")


@app.get("/health")
def health():
    return {"status": "ok", "models_loaded": len(_bundle)}


@app.get("/predict/{product_id}")
def predict(product_id: int):
    if product_id not in _bundle:
        raise HTTPException(status_code=404, detail="No trained model for this product")

    raw = pd.read_sql(
        "SELECT sold_at, qty FROM sales WHERE product_id = %(pid)s ORDER BY sold_at",
        engine, params={"pid": product_id},
    )
    raw = raw.groupby("sold_at", as_index=False)["qty"].sum()
    today = date.today()
    history = fill_daily_gaps(raw, raw["sold_at"].min(), today - timedelta(days=1))
    featured = build_features(history)
    trend = featured.iloc[-1]["rolling_7_avg"]  # reused for all 7 days — ch8 keeps this simple on purpose
    model = _bundle[product_id]

    forecast = []
    for i in range(1, 8):
        target = today + timedelta(days=i)
        lag_row = history[history["sold_at"] == pd.Timestamp(target - timedelta(days=7))]
        lag_7 = lag_row["qty"].values[0] if not lag_row.empty else featured["qty"].tail(7).mean()
        row = pd.DataFrame([{
            "day_of_week": target.weekday(), "day_of_month": target.day,
            "lag_7": lag_7, "rolling_7_avg": trend,
        }])
        qty = max(0, round(model.predict(row[FEATURE_COLUMNS])[0]))
        forecast.append({"date": str(target), "predicted_qty": qty})

    return {"product_id": product_id, "forecast": forecast}