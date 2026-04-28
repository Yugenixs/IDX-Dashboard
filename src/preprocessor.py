"""
Preprocessing Layer
Handles data cleaning and format normalization.
"""

import pandas as pd


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    ohlcv_cols = ["Open", "High", "Low", "Close", "Volume"]
    df = df.dropna(subset=ohlcv_cols, how="all").copy()
    for col in ["Open", "High", "Low", "Close", "Adj Close"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").ffill()
    df["Volume"] = pd.to_numeric(df["Volume"], errors="coerce").fillna(0).astype(int)
    return df.reset_index(drop=True)


def filter_by_date(df: pd.DataFrame, start, end) -> pd.DataFrame:
    mask = (df["Date"].dt.date >= start) & (df["Date"].dt.date <= end)
    return df.loc[mask].reset_index(drop=True)
