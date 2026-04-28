import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st
import pandas as pd
import numpy as np

from src.data_loader import load_all_stocks, get_date_range, STOCK_META
from src.preprocessor import clean_data, filter_by_date
from src.feature_engineering import build_features
from src.charts import (
    candlestick_chart, cumulative_return_chart, daily_return_histogram,
    volatility_chart, drawdown_chart, monthly_returns_chart,
    multi_cumulative_return, multi_price_normalized,
    performance_bar_chart, volatility_comparison_bar,
    correlation_heatmap, sector_performance_chart,
)

st.set_page_config(
    page_title="IDX Dashboard 2025",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
  /* ---------- global ---------- */
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

  html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, sans-serif !important;
  }

  .main .block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
    max-width: 1400px;
  }

  /* ---------- sidebar ---------- */
  [data-testid="stSidebar"] {
    background: #FFFFFF;
    border-right: 1px solid #E5E7EB;
  }
  [data-testid="stSidebar"] .block-container { padding: 1.5rem 1rem; }

  /* ---------- metric cards ---------- */
  [data-testid="stMetric"] {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 12px;
    padding: 1rem 1.2rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
  }
  [data-testid="stMetricLabel"]  { font-size: 0.78rem; color: #6B7280; font-weight: 500; }
  [data-testid="stMetricValue"]  { font-size: 1.5rem;  color: #1A1D2E; font-weight: 700; }
  [data-testid="stMetricDelta"]  { font-size: 0.82rem; }

  /* ---------- plotly chart container ---------- */
  [data-testid="stPlotlyChart"] {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 12px;
    padding: 0.5rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
  }

  /* ---------- dataframe ---------- */
  [data-testid="stDataFrame"] {
    border: 1px solid #E5E7EB;
    border-radius: 10px;
    overflow: hidden;
  }

  /* ---------- tabs ---------- */
  [data-testid="stTabs"] button {
    font-size: 0.88rem;
    font-weight: 500;
    color: #6B7280;
    padding: 0.5rem 1.2rem;
    border-radius: 8px 8px 0 0;
  }
  [data-testid="stTabs"] button[aria-selected="true"] {
    color: #6C63FF;
    border-bottom: 2px solid #6C63FF;
    font-weight: 600;
  }

  /* ---------- section title ---------- */
  .section-title {
    font-size: 1rem;
    font-weight: 600;
    color: #1A1D2E;
    margin-bottom: 0.5rem;
    padding-left: 2px;
  }

  /* ---------- badge pill ---------- */
  .badge {
    display: inline-block;
    background: #EEF2FF;
    color: #6C63FF;
    border-radius: 20px;
    padding: 2px 10px;
    font-size: 0.72rem;
    font-weight: 600;
    margin-left: 6px;
    vertical-align: middle;
  }

  .badge-green  { background: #DCFCE7; color: #16A34A; }
  .badge-red    { background: #FEE2E2; color: #DC2626; }
  .badge-yellow { background: #FEF3C7; color: #D97706; }

  /* ---------- page header ---------- */
  .page-header {
    background: linear-gradient(135deg, #6C63FF 0%, #4A90D9 100%);
    border-radius: 16px;
    padding: 1.5rem 2rem;
    margin-bottom: 1.5rem;
    color: white;
  }
  .page-header h1 { margin: 0; font-size: 1.6rem; font-weight: 700; color: white; }
  .page-header p  { margin: 0.3rem 0 0; font-size: 0.88rem; opacity: 0.85; color: white; }

  /* ---------- divider ---------- */
  hr { border: none; border-top: 1px solid #E5E7EB; margin: 1rem 0; }

  /* ---------- card wrapper ---------- */
  .card {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 12px;
    padding: 1.25rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    margin-bottom: 1rem;
  }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def get_all_data() -> dict[str, pd.DataFrame]:
    raw = load_all_stocks()
    return {ticker: build_features(clean_data(df)) for ticker, df in raw.items()}


all_data = get_all_data()
tickers   = list(all_data.keys())
first_df  = next(iter(all_data.values()))
min_date, max_date = get_date_range(first_df)


with st.sidebar:
    st.markdown("## IDX Dashboard")
    st.caption("Bursa Efek Indonesia · 2025")
    st.markdown("---")

    page = st.radio(
        "Navigasi",
        ["Market Overview", "Analisis Saham", "Perbandingan"],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown("**Filter Periode**")
    start_date = st.date_input("Dari",    value=min_date, min_value=min_date, max_value=max_date)
    end_date   = st.date_input("Sampai",  value=max_date, min_value=min_date, max_value=max_date)

    if start_date > end_date:
        st.error("Tanggal awal > akhir")
        st.stop()

    if page == "Analisis Saham":
        st.markdown("---")
        st.markdown("**Pilih Saham**")
        selected_ticker = st.selectbox(
            "Saham",
            tickers,
            format_func=lambda t: f"{t.replace('.JK','')} — {STOCK_META[t]['name']}",
            label_visibility="collapsed",
        )
        show_ma = st.toggle("MA20 / MA50", value=True)

    if page == "Perbandingan":
        st.markdown("---")
        st.markdown("**Pilih Saham (min 2)**")
        compare_tickers = st.multiselect(
            "Saham",
            tickers,
            default=tickers[:5],
            format_func=lambda t: t.replace(".JK", ""),
            label_visibility="collapsed",
        )
        if len(compare_tickers) < 2:
            st.warning("Pilih minimal 2 saham")

    st.markdown("---")
    st.caption("Data bersumber dari Yahoo Finance, digunakan untuk tujuan edukasi dan pengembangan portfolio. Lakukan riset mandiri (DYOR) sebelum mengambil keputusan.")


def filtered(ticker: str) -> pd.DataFrame:
    df = filter_by_date(all_data[ticker], start_date, end_date).copy()
    if not df.empty:
        df["Cumulative Return (%)"] = ((df["Close"] / df["Close"].iloc[0]) - 1) * 100
    return df


def build_summary() -> pd.DataFrame:
    rows = []
    for ticker in tickers:
        df = filtered(ticker)
        if df.empty:
            continue
        ret = df["Daily Return (%)"].dropna()
        ytd = ((df["Close"].iloc[-1] / df["Close"].iloc[0]) - 1) * 100
        rows.append({
            "Ticker":        ticker.replace(".JK", ""),
            "Nama":          STOCK_META[ticker]["name"],
            "Sector":        STOCK_META[ticker]["sector"],
            "Harga Awal":    df["Close"].iloc[0],
            "Harga Akhir":   df["Close"].iloc[-1],
            "YTD Return (%)":round(ytd, 2),
            "Volatility (%)":round(ret.std() * np.sqrt(252) * 100, 2) if len(ret) > 1 else 0,
            "Max Drawdown (%)": round(df["Drawdown (%)"].min(), 2) if "Drawdown (%)" in df.columns else 0,
            "Avg Volume":    int(df["Volume"].mean()),
        })
    return pd.DataFrame(rows)

if page == "Market Overview":
    st.markdown(f"""
<div class="page-header">
<h1>IDX Top 10 Saham — Market Overview 2025</h1>
<p>Bursa Efek Indonesia · {start_date.strftime('%d %b %Y')} — {end_date.strftime('%d %b %Y')} · 10 Emiten</p>
</div>
""", unsafe_allow_html=True)

    summary = build_summary()

    # ── KPI row ──────────────────────────────────────────────────────────────
    best   = summary.loc[summary["YTD Return (%)"].idxmax()]
    worst  = summary.loc[summary["YTD Return (%)"].idxmin()]
    most_vol   = summary.loc[summary["Volatility (%)"].idxmax()]
    least_vol  = summary.loc[summary["Volatility (%)"].idxmin()]
    avg_ret    = summary["YTD Return (%)"].mean()

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Best Performer",  best["Ticker"],  f"{best['YTD Return (%)']:+.2f}%")
    c2.metric("Worst Performer", worst["Ticker"], f"{worst['YTD Return (%)']:+.2f}%")
    c3.metric("Avg YTD Return",  f"{avg_ret:+.2f}%")
    c4.metric("Paling Volatile", most_vol["Ticker"],  f"{most_vol['Volatility (%)']:.1f}%")
    c5.metric("Paling Stabil",   least_vol["Ticker"], f"{least_vol['Volatility (%)']:.1f}%")

    st.markdown("<br>", unsafe_allow_html=True)

    col_l, col_r = st.columns(2)
    with col_l:
        filtered_stocks = {t: filtered(t) for t in tickers}
        st.plotly_chart(performance_bar_chart(summary), use_container_width=True)
    with col_r:
        st.plotly_chart(sector_performance_chart(summary), use_container_width=True)

    st.plotly_chart(multi_price_normalized(filtered_stocks), use_container_width=True)

    st.markdown('<p class="section-title">Tabel Ringkasan Semua Saham</p>', unsafe_allow_html=True)
    disp = summary.copy()
    disp["Harga Awal"]   = disp["Harga Awal"].map(lambda x: f"IDR {x:,.0f}")
    disp["Harga Akhir"]  = disp["Harga Akhir"].map(lambda x: f"IDR {x:,.0f}")
    disp["YTD Return (%)"]    = disp["YTD Return (%)"].map(lambda x: f"{x:+.2f}%")
    disp["Volatility (%)"]    = disp["Volatility (%)"].map(lambda x: f"{x:.1f}%")
    disp["Max Drawdown (%)"]  = disp["Max Drawdown (%)"].map(lambda x: f"{x:.2f}%")
    disp["Avg Volume"]        = disp["Avg Volume"].map(lambda x: f"{x:,.0f}")
    st.dataframe(
        disp[["Ticker","Nama","Sector","Harga Awal","Harga Akhir",
              "YTD Return (%)","Volatility (%)","Max Drawdown (%)","Avg Volume"]],
        use_container_width=True, hide_index=True, height=380,
    )

elif page == "Analisis Saham":
    meta  = STOCK_META[selected_ticker]
    df    = filtered(selected_ticker)

    badge_color = "badge-green" if ((df["Close"].iloc[-1] / df["Close"].iloc[0]) - 1) >= 0 else "badge-red"
    ytd   = ((df["Close"].iloc[-1] / df["Close"].iloc[0]) - 1) * 100

    st.markdown(f"""
<div class="page-header">
<h1>{selected_ticker.replace('.JK','')} — {meta['name']}
<span class="badge {badge_color}">{ytd:+.2f}%</span>
</h1>
<p>{meta['sector']} · Bursa Efek Indonesia · {start_date.strftime('%d %b %Y')} — {end_date.strftime('%d %b %Y')}</p>
</div>
""", unsafe_allow_html=True)

    if df.empty:
        st.warning("Tidak ada data untuk periode ini.")
        st.stop()

    ret_series = df["Daily Return (%)"].dropna()
    vol_ann    = ret_series.std() * np.sqrt(252) * 100 if len(ret_series) > 1 else 0
    max_dd     = df["Drawdown (%)"].min() if "Drawdown (%)" in df.columns else 0
    pos_days   = (ret_series > 0).sum()
    neg_days   = (ret_series < 0).sum()

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Harga Terakhir",  f"IDR {df['Close'].iloc[-1]:,.0f}", f"{ytd:+.2f}% (periode)")
    c2.metric("Harga Tertinggi", f"IDR {df['High'].max():,.0f}")
    c3.metric("Harga Terendah",  f"IDR {df['Low'].min():,.0f}")
    c4.metric("Volatilitas", f"{vol_ann:.1f}%")
    c5.metric("Max Drawdown",    f"{max_dd:.2f}%")
    c6.metric("Win Rate",        f"{pos_days/(pos_days+neg_days)*100:.1f}%" if (pos_days+neg_days) > 0 else "—")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Tabs ─────────────────────────────────────────────────────────────────
    tab1, tab2, tab3 = st.tabs(["Price Action", "Returns & Risk", "Monthly"])

    with tab1:
        st.plotly_chart(candlestick_chart(df, show_ma=show_ma, ticker=selected_ticker.replace(".JK","")), use_container_width=True)

        st.markdown('<p class="section-title">Data Historis</p>', unsafe_allow_html=True)
        show_cols = ["Date","Open","High","Low","Close","Volume","Daily Return (%)"]
        show_cols = [c for c in show_cols if c in df.columns]
        tdf = df[show_cols].copy()
        tdf["Date"] = tdf["Date"].dt.strftime("%Y-%m-%d")
        if "Daily Return (%)" in tdf.columns:
            tdf["Daily Return (%)"] = tdf["Daily Return (%)"].map(
                lambda x: f"{x:+.2f}%" if pd.notna(x) else ""
            )
        st.dataframe(tdf.sort_values("Date", ascending=False).reset_index(drop=True),
                     use_container_width=True, height=300)

    with tab2:
        col_a, col_b = st.columns(2)
        with col_a:
            st.plotly_chart(cumulative_return_chart(df, ticker=selected_ticker.replace(".JK","")), use_container_width=True)
        with col_b:
            st.plotly_chart(daily_return_histogram(df, ticker=selected_ticker.replace(".JK","")), use_container_width=True)

        col_c, col_d = st.columns(2)
        with col_c:
            st.plotly_chart(volatility_chart(df, ticker=selected_ticker.replace(".JK","")), use_container_width=True)
        with col_d:
            st.plotly_chart(drawdown_chart(df, ticker=selected_ticker.replace(".JK","")), use_container_width=True)

        st.markdown('<p class="section-title">Ringkasan Statistik</p>', unsafe_allow_html=True)
        stats = {
            "Mean Daily Return":     f"{ret_series.mean():.4f}%",
            "Median Daily Return":   f"{ret_series.median():.4f}%",
            "Std Dev Daily":         f"{ret_series.std():.4f}%",
            "Annualised Volatility": f"{vol_ann:.2f}%",
            "Best Single Day":       f"{ret_series.max():+.2f}%",
            "Worst Single Day":      f"{ret_series.min():+.2f}%",
            "Positive Days":         f"{pos_days} hari",
            "Negative Days":         f"{neg_days} hari",
            "Win Rate":              f"{pos_days/(pos_days+neg_days)*100:.1f}%" if (pos_days+neg_days) > 0 else "—",
            "Max Drawdown":          f"{max_dd:.2f}%",
            "Cumulative Return":     f"{ytd:+.2f}%",
        }
        stats_df = pd.DataFrame(list(stats.items()), columns=["Metrik", "Nilai"])
        st.dataframe(stats_df, use_container_width=True, hide_index=True)

    with tab3:
        st.plotly_chart(monthly_returns_chart(df, ticker=selected_ticker.replace(".JK","")), use_container_width=True)

        temp = df.copy()
        temp["Month"] = temp["Date"].dt.to_period("M")
        monthly_tbl = (
            temp.groupby("Month")["Close"]
            .agg(["first", "last"])
            .assign(ret=lambda x: (x["last"] / x["first"] - 1) * 100)
            .reset_index()
            .rename(columns={"Month": "Bulan", "ret": "Return (%)"})
        )
        monthly_tbl["Harga Awal"]  = monthly_tbl["first"].map(lambda x: f"IDR {x:,.0f}")
        monthly_tbl["Harga Akhir"] = monthly_tbl["last"].map(lambda x: f"IDR {x:,.0f}")
        monthly_tbl["Return (%)"]  = monthly_tbl["Return (%)"].map(lambda x: f"{x:+.2f}%")
        monthly_tbl["Bulan"]       = monthly_tbl["Bulan"].astype(str)
        st.dataframe(
            monthly_tbl[["Bulan","Harga Awal","Harga Akhir","Return (%)"]],
            use_container_width=True, hide_index=True,
        )

elif page == "Perbandingan":
    if len(compare_tickers) < 2:
        st.info("Pilih minimal 2 saham dari sidebar untuk mulai perbandingan.")
        st.stop()

    st.markdown(f"""
<div class="page-header">
<h1>Perbandingan Saham</h1>
<p>{' · '.join(t.replace('.JK','') for t in compare_tickers)} · {start_date.strftime('%d %b %Y')} — {end_date.strftime('%d %b %Y')}</p>
</div>
""", unsafe_allow_html=True)

    comp_data = {t: filtered(t) for t in compare_tickers}
    comp_summary = build_summary()
    comp_summary = comp_summary[comp_summary["Ticker"].isin([t.replace(".JK","") for t in compare_tickers])]

    best_c  = comp_summary.loc[comp_summary["YTD Return (%)"].idxmax()]
    worst_c = comp_summary.loc[comp_summary["YTD Return (%)"].idxmin()]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Best (pilihan)",  best_c["Ticker"],  f"{best_c['YTD Return (%)']:+.2f}%")
    c2.metric("Worst (pilihan)", worst_c["Ticker"], f"{worst_c['YTD Return (%)']:+.2f}%")
    c3.metric("Avg YTD Return",  f"{comp_summary['YTD Return (%)'].mean():+.2f}%")
    c4.metric("Saham dipilih",   f"{len(compare_tickers)} saham")

    st.markdown("<br>", unsafe_allow_html=True)

    tab_a, tab_b, tab_c = st.tabs(["Return Comparison", "Risk & Volatility", "Korelasi"])

    with tab_a:
        st.plotly_chart(multi_cumulative_return(comp_data), use_container_width=True)
        st.plotly_chart(multi_price_normalized(comp_data),  use_container_width=True)

        st.markdown('<p class="section-title">Tabel Perbandingan</p>', unsafe_allow_html=True)
        disp2 = comp_summary.copy()
        disp2["Harga Awal"]       = disp2["Harga Awal"].map(lambda x: f"IDR {x:,.0f}")
        disp2["Harga Akhir"]      = disp2["Harga Akhir"].map(lambda x: f"IDR {x:,.0f}")
        disp2["YTD Return (%)"]   = disp2["YTD Return (%)"].map(lambda x: f"{x:+.2f}%")
        disp2["Volatility (%)"]   = disp2["Volatility (%)"].map(lambda x: f"{x:.1f}%")
        disp2["Max Drawdown (%)"] = disp2["Max Drawdown (%)"].map(lambda x: f"{x:.2f}%")
        st.dataframe(
            disp2[["Ticker","Nama","Sector","Harga Awal","Harga Akhir",
                   "YTD Return (%)","Volatility (%)","Max Drawdown (%)"]],
            use_container_width=True, hide_index=True,
        )

    with tab_b:
        col_l, col_r = st.columns(2)
        with col_l:
            st.plotly_chart(performance_bar_chart(comp_summary), use_container_width=True)
        with col_r:
            st.plotly_chart(volatility_comparison_bar(comp_summary), use_container_width=True)

    with tab_c:
        price_matrix = pd.DataFrame({
            t: comp_data[t].set_index("Date")["Close"]
            for t in compare_tickers if not comp_data[t].empty
        })
        if price_matrix.shape[1] >= 2:
            st.plotly_chart(correlation_heatmap(price_matrix), use_container_width=True)
            st.markdown("""
<div class="card">
<b>Cara membaca korelasi:</b><br>
<code>+1.0</code> → bergerak searah sempurna &nbsp;|&nbsp;
<code>0.0</code> → tidak ada hubungan &nbsp;|&nbsp;
<code>-1.0</code> → bergerak berlawanan arah<br>
Saham perbankan (BBCA, BBRI, BMRI, BBNI) cenderung berkorelasi tinggi.
</div>
""", unsafe_allow_html=True)
        else:
            st.info("Pilih lebih banyak saham untuk melihat matriks korelasi.")

st.markdown("---")
footer = """
<div style="text-align: center; padding: 10px 0; font-size: 14px; color: #888;">
<div style="font-weight: 600; color: #ccc;">
IDX Top 10 Dashboard · Portfolio Project 2025
</div>
<div style="margin-top: 6px;">
Developed by <b>Ilyas Tio Afrilian (Yugenix)</b>
</div>
<div style="margin-top: 4px;">
Data source: Yahoo Finance
</div>
<div style="margin-top: 8px; font-size: 12px; color: #666;">
For educational and portfolio purposes only · Always do your own research (DYOR)
</div>
</div>
"""

st.markdown(footer, unsafe_allow_html=True)
