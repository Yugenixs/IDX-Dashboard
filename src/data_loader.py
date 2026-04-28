import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"

STOCK_META = {
    "BBCA.JK": {"name": "Bank Central Asia",     "sector": "Perbankan"},
    "BBRI.JK": {"name": "Bank Rakyat Indonesia", "sector": "Perbankan"},
    "BMRI.JK": {"name": "Bank Mandiri",           "sector": "Perbankan"},
    "BBNI.JK": {"name": "Bank Negara Indonesia",  "sector": "Perbankan"},
    "TLKM.JK": {"name": "Telkom Indonesia",       "sector": "Telekomunikasi"},
    "TOWR.JK": {"name": "Sarana Menara Nusantara","sector": "Telekomunikasi"},
    "ISAT.JK": {"name": "Indosat Ooredoo",        "sector": "Telekomunikasi"},
    "ASII.JK": {"name": "Astra International",    "sector": "Otomotif & Multi"},
    "UNVR.JK": {"name": "Unilever Indonesia",     "sector": "Consumer Goods"},
    "ICBP.JK": {"name": "Indofood CBP Sukses",    "sector": "Consumer Goods"},
}


def _csv_path(ticker: str) -> Path:
    return DATA_DIR / f"{ticker.replace('.', '_')}_2025.csv"


def load_stock(ticker: str) -> pd.DataFrame:
    """Load and sort a single stock CSV."""
    path = _csv_path(ticker)
    df = pd.read_csv(path, parse_dates=["Date"])
    df = df.sort_values("Date").reset_index(drop=True)
    df.columns = [c.strip() for c in df.columns]
    return df


def load_all_stocks() -> dict[str, pd.DataFrame]:
    """Return {ticker: DataFrame} for all available tickers."""
    result = {}
    for ticker in STOCK_META:
        path = _csv_path(ticker)
        if path.exists():
            result[ticker] = load_stock(ticker)
    return result


def get_date_range(df: pd.DataFrame) -> tuple:
    return df["Date"].min().date(), df["Date"].max().date()
