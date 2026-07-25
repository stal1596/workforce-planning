import os
from datetime import date

import joblib
import pandas as pd
from dotenv import load_dotenv
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error
from sqlalchemy import create_engine

from features import FEATURE_COLUMNS, build_features, fill_daily_gaps

load_dotenv()
engine = create_engine(os.environ["DATABASE_URL"])
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
TEST_DAYS = 7


def load_product_history(product_id: int) -> pd.DataFrame:
    df = pd.read_sql(
        "SELECT sold_at, qty FROM sales WHERE product_id = %(pid)s ORDER BY sold_at",
        engine, params={"pid": product_id},
    )
    if df.empty:
        return df
    df = df.groupby("sold_at", as_index=False)["qty"].sum()
    return fill_daily_gaps(df, df["sold_at"].min(), df["sold_at"].max())


def naive_baseline_mae(df: pd.DataFrame, test_start_idx: int) -> float:
    """ch8's mock exam: average of the last 4 same-weekdays, computed only
    from data BEFORE each test point."""
    preds, actuals = [], []
    for i in range(test_start_idx, len(df)):
        same_wd = df[df["day_of_week"] == df.iloc[i]["day_of_week"]]
        history = same_wd[same_wd.index < i].tail(4)
        if history.empty:
            continue
        preds.append(history["qty"].mean())
        actuals.append(df.iloc[i]["qty"])
    return mean_absolute_error(actuals, preds) if actuals else float("inf")


def train_for_product(product_id: int, name: str):
    raw = load_product_history(product_id)
    if len(raw) < 30:
        print(f"  skip {name}: only {len(raw)} days of history, need 30+")
        return None

    df = build_features(raw).dropna(subset=FEATURE_COLUMNS)
    split = len(df) - TEST_DAYS
    train_df, test_df = df.iloc[:split], df.iloc[split:]

    model = GradientBoostingRegressor(random_state=42)
    model.fit(train_df[FEATURE_COLUMNS], train_df["qty"])
    model_mae = mean_absolute_error(test_df["qty"], model.predict(test_df[FEATURE_COLUMNS]))
    baseline_mae = naive_baseline_mae(df, split)

    print(f"  {name}: model MAE={model_mae:.2f}  baseline MAE={baseline_mae:.2f}")
    if model_mae >= baseline_mae:
        print("  -> did not beat the naive baseline, not saving")
        return None
    return {"product_id": product_id, "model": model, "mae": model_mae}


def main():
    products = pd.read_sql("SELECT id, name FROM products", engine)
    version = date.today().strftime("v%Y%m%d")
    os.makedirs(MODEL_DIR, exist_ok=True)

    results = []
    for _, row in products.iterrows():
        print(f"Training: {row['name']}")
        r = train_for_product(row["id"], row["name"])
        if r:
            results.append(r)

    if not results:
        print("Nothing beat its baseline — champion unchanged, nothing saved.")
        return

    bundle = {r["product_id"]: r["model"] for r in results}
    filename = f"model_{version}.pkl"
    joblib.dump(bundle, os.path.join(MODEL_DIR, filename))
    with open(os.path.join(MODEL_DIR, "production.txt"), "w") as f:
        f.write(filename)

    maes = ";".join(f"{r['product_id']}:{r['mae']:.2f}" for r in results)
    with open(os.path.join(MODEL_DIR, "runs.csv"), "a") as f:
        f.write(f"{date.today()},{version},{len(results)}/{len(products)},{maes}\n")

    print(f"Saved {filename} — {len(results)}/{len(products)} products beat baseline.")


if __name__ == "__main__":
    main()