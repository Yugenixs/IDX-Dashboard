"""
Feature Engineering Layer
Computes derived metrics. Works on a single DataFrame.
"""

import pandas as pd
import numpy as np


def add_daily_return(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Daily Return (%)"] = df["Close"].pct_change() * 100
    return df


def add_cumulative_return(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if len(df) == 0:
        df["Cumulative Return (%)"] = pd.Series(dtype=float)
        return df
    df["Cumulative Return (%)"] = ((df["Close"] / df["Close"].iloc[0]) - 1) * 100
    return df


def add_moving_averages(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["MA20"] = df["Close"].rolling(window=20, min_periods=1).mean()
    df["MA50"] = df["Close"].rolling(window=50, min_periods=1).mean()
    return df


def add_volatility(df: pd.DataFrame, window: int = 20) -> pd.DataFrame:
    df = df.copy()
    daily_ret = df["Close"].pct_change()
    df[f"Volatility {window}d (%)"] = (
        daily_ret.rolling(window=window, min_periods=2).std() * np.sqrt(252) * 100
    )
    return df


def add_drawdown(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    rolling_max = df["Close"].cummax()
    df["Drawdown (%)"] = ((df["Close"] - rolling_max) / rolling_max) * 100
    return df


def add_volume_ma(df: pd.DataFrame, window: int = 20) -> pd.DataFrame:
    df = df.copy()
    df["Volume MA20"] = df["Volume"].rolling(window=window, min_periods=1).mean()
    return df


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    df = add_daily_return(df)
    df = add_cumulative_return(df)
    df = add_moving_averages(df)
    df = add_volatility(df)
    df = add_drawdown(df)
    df = add_volume_ma(df)
    return df
