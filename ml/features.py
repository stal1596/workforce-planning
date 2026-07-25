import pandas as pd

FEATURE_COLUMNS = ["day_of_week", "day_of_month", "lag_7", "rolling_7_avg"]


def fill_daily_gaps(sales_df: pd.DataFrame, start, end) -> pd.DataFrame:
    """Sales rows only exist for days something sold. A model can't learn from
    a day that silently doesn't exist — reindex to one row per calendar day,
    missing days = 0 sold."""
    df = sales_df.set_index("sold_at").reindex(pd.date_range(start, end, freq="D"), fill_value=0)
    df.index.name = "sold_at"
    return df.reset_index()


def build_features(sales_df: pd.DataFrame) -> pd.DataFrame:
    """sales_df: ['sold_at', 'qty'], one row per day, no gaps, sorted ascending.
    Used by BOTH train.py and serve.py — this is the vaccine against
    training/serving skew ch8 warns about. Change it once, both worlds change."""
    df = sales_df.copy()
    df["sold_at"] = pd.to_datetime(df["sold_at"])
    df = df.sort_values("sold_at").reset_index(drop=True)
    df["day_of_week"] = df["sold_at"].dt.dayofweek
    df["day_of_month"] = df["sold_at"].dt.day
    df["lag_7"] = df["qty"].shift(7)
    df["rolling_7_avg"] = df["qty"].shift(1).rolling(7).mean()
    return df