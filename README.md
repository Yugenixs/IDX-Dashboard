# IDX Top 10 Dashboard — 2025

Historical analysis of 10 blue-chip stocks on the Indonesia Stock Exchange throughout 2025 — returns, volatility, drawdown, and correlation — in a single interactive dashboard.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app.streamlit.app)

---

## Features

| Module | Description |
|---|---|
| **Market Overview** | YTD return, volatility, and performance comparison across all 10 stocks at once |
| **Individual Analysis** | Candlestick chart with MA20/MA50, return distribution, rolling volatility, drawdown, and monthly breakdown per stock |
| **Multi-Stock Comparison** | Cumulative return overlay, normalized price chart, and cross-stock correlation heatmap |
| **Interactive Filters** | Date range selector and stock picker via sidebar |

## Coverage

| Ticker | Company | Sector |
|---|---|---|
| BBCA.JK | Bank Central Asia | Banking |
| BBRI.JK | Bank Rakyat Indonesia | Banking |
| BMRI.JK | Bank Mandiri | Banking |
| BBNI.JK | Bank Negara Indonesia | Banking |
| TLKM.JK | Telkom Indonesia | Telecommunications |
| TOWR.JK | Sarana Menara Nusantara | Telecommunications |
| ISAT.JK | Indosat Ooredoo Hutchison | Telecommunications |
| ASII.JK | Astra International | Automotive & Multi |
| UNVR.JK | Unilever Indonesia | Consumer Goods |
| ICBP.JK | Indofood CBP Sukses Makmur | Consumer Goods |

## Tech Stack

| Library | Role |
|---|---|
| Streamlit | UI framework |
| Pandas | Data processing |
| Plotly | Interactive charts |
| NumPy | Numerical computation |

Requires Python 3.9+

## Project Structure

```
stock-dashboard/
├── .streamlit/
│   └── config.toml              # Theme and server configuration
├── data/
│   └── *.csv                    # Yahoo Finance historical data (10 files)
├── src/
│   ├── __init__.py
│   ├── data_loader.py           # Load CSV files
│   ├── preprocessor.py          # Cleaning and date filtering
│   ├── feature_engineering.py   # Returns, MA, volatility, drawdown
│   └── charts.py                # All Plotly figures
├── app.py                       # Streamlit entry point
└── requirements.txt
```

## Run Locally

```bash
git clone https://github.com/username/idx-dashboard.git
cd idx-dashboard
pip install -r requirements.txt
streamlit run app.py
```

## Deploy to Streamlit Community Cloud

1. Push the repo to GitHub — make sure the `data/` folder is committed
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**
3. Select the repo, set **Main file path** to `app.py`
4. Click **Deploy**

## Data

Historical price data sourced from Yahoo Finance, stored as static CSV files in `data/`. No internet connection required at runtime.

---

> **Disclaimer:** Built for educational purposes. Not investment advice.

---

## Contact

- Email: yugenix555@gmail.com
- Twitter: [@yugenixs](https://twitter.com/yugenixs)
- GitHub: [@yugenixs](https://github.com/yugenixs)
  
Developed by **Ilyas Tio Afrilian**
