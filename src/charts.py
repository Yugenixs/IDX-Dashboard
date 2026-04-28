import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

_C = {
    "primary":    "#6C63FF",
    "secondary":  "#4A90D9",
    "accent":     "#A78BFA",
    "up":         "#22C55E",
    "down":       "#EF4444",
    "warn":       "#F59E0B",
    "bg":         "#FFFFFF",
    "surface":    "#F5F6FA",
    "border":     "#E5E7EB",
    "text":       "#1A1D2E",
    "text_muted": "#6B7280",
}

STOCK_COLORS = [
    "#6C63FF", "#4A90D9", "#22C55E", "#F59E0B", "#EF4444",
    "#8B5CF6", "#06B6D4", "#EC4899", "#14B8A6", "#F97316",
]

_BASE = dict(
    template="plotly_white",
    paper_bgcolor=_C["bg"],
    plot_bgcolor=_C["surface"],
    font=dict(family="Inter, -apple-system, sans-serif", size=12, color=_C["text"]),
    margin=dict(l=50, r=20, t=48, b=40),
    xaxis=dict(showgrid=True, gridcolor=_C["border"], linecolor=_C["border"]),
    yaxis=dict(showgrid=True, gridcolor=_C["border"], linecolor=_C["border"]),
    legend=dict(bgcolor="rgba(255,255,255,0.9)", bordercolor=_C["border"], borderwidth=1),
)

_LEGEND_H = dict(
    bgcolor="rgba(255,255,255,0.9)",
    bordercolor=_C["border"],
    borderwidth=1,
    orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="right",
    x=1,
)


def _layout(**overrides) -> dict:
    return {**_BASE, **overrides}

def candlestick_chart(df: pd.DataFrame, show_ma: bool = True, ticker: str = "") -> go.Figure:
    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True,
        row_heights=[0.72, 0.28], vertical_spacing=0.04,
    )
    fig.add_trace(go.Candlestick(
        x=df["Date"], open=df["Open"], high=df["High"],
        low=df["Low"], close=df["Close"],
        name=ticker or "Harga",
        increasing_line_color=_C["up"], decreasing_line_color=_C["down"],
        increasing_fillcolor=_C["up"], decreasing_fillcolor=_C["down"],
    ), row=1, col=1)

    if show_ma and "MA20" in df.columns:
        fig.add_trace(go.Scatter(
            x=df["Date"], y=df["MA20"], name="MA20",
            line=dict(color=_C["warn"], width=1.8),
        ), row=1, col=1)
    if show_ma and "MA50" in df.columns:
        fig.add_trace(go.Scatter(
            x=df["Date"], y=df["MA50"], name="MA50",
            line=dict(color=_C["primary"], width=1.8, dash="dot"),
        ), row=1, col=1)

    bar_colors = [
        _C["up"] if c >= o else _C["down"]
        for c, o in zip(df["Close"], df["Open"])
    ]
    fig.add_trace(go.Bar(
        x=df["Date"], y=df["Volume"], name="Volume",
        marker_color=bar_colors, opacity=0.6, showlegend=False,
    ), row=2, col=1)

    if "Volume MA20" in df.columns:
        fig.add_trace(go.Scatter(
            x=df["Date"], y=df["Volume MA20"], name="Vol MA20",
            line=dict(color=_C["primary"], width=1.5, dash="dash"),
            showlegend=False,
        ), row=2, col=1)

    fig.update_layout(**_layout(
        title=dict(text=f"{ticker} — Price Action & Volume", font=dict(size=15, color=_C["text"])),
        xaxis_rangeslider_visible=False,
        height=520,
        legend=_LEGEND_H,
    ))
    fig.update_yaxes(title_text="Harga (IDR)", gridcolor=_C["border"], row=1, col=1)
    fig.update_yaxes(title_text="Volume",      gridcolor=_C["border"], row=2, col=1)
    return fig


def cumulative_return_chart(df: pd.DataFrame, ticker: str = "") -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["Date"], y=df["Cumulative Return (%)"],
        fill="tozeroy", name="Cumulative Return",
        line=dict(color=_C["primary"], width=2.5),
        fillcolor="rgba(108,99,255,0.12)",
    ))
    fig.add_hline(y=0, line_dash="dash", line_color=_C["text_muted"], line_width=1)
    fig.update_layout(**_layout(
        title=dict(text=f"{ticker} — Cumulative Return (%)", font=dict(size=15)),
        yaxis_title="Return (%)", height=340,
    ))
    return fig


def daily_return_histogram(df: pd.DataFrame, ticker: str = "") -> go.Figure:
    ret = df["Daily Return (%)"].dropna()
    mean_r = ret.mean()
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=ret, nbinsx=40,
        marker=dict(color=_C["secondary"], opacity=0.8),
        name="Daily Return",
    ))
    fig.add_vline(
        x=mean_r, line_dash="dash", line_color=_C["primary"], line_width=2,
        annotation_text=f"Mean: {mean_r:.2f}%",
        annotation_font_color=_C["primary"],
        annotation_position="top right",
    )
    fig.update_layout(**_layout(
        title=dict(text=f"{ticker} — Distribusi Daily Return", font=dict(size=15)),
        xaxis_title="Return (%)", yaxis_title="Frekuensi", height=340,
    ))
    return fig


def volatility_chart(df: pd.DataFrame, ticker: str = "") -> go.Figure:
    col = "Volatility 20d (%)"
    data = df[col] if col in df.columns else pd.Series(dtype=float)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["Date"], y=data,
        fill="tozeroy", name="20d Volatility",
        line=dict(color=_C["accent"], width=2),
        fillcolor="rgba(167,139,250,0.15)",
    ))
    fig.update_layout(**_layout(
        title=dict(text=f"{ticker} — Rolling 20-Day Volatility (Annualised)", font=dict(size=15)),
        yaxis_title="Volatility (%)", height=300,
    ))
    return fig


def drawdown_chart(df: pd.DataFrame, ticker: str = "") -> go.Figure:
    data = df["Drawdown (%)"] if "Drawdown (%)" in df.columns else pd.Series(dtype=float)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["Date"], y=data,
        fill="tozeroy", name="Drawdown",
        line=dict(color=_C["down"], width=1.8),
        fillcolor="rgba(239,68,68,0.15)",
    ))
    fig.update_layout(**_layout(
        title=dict(text=f"{ticker} — Drawdown dari Peak", font=dict(size=15)),
        yaxis_title="Drawdown (%)", height=300,
    ))
    return fig


def monthly_returns_chart(df: pd.DataFrame, ticker: str = "") -> go.Figure:
    temp = df.copy()
    temp["Month"] = temp["Date"].dt.to_period("M")
    monthly = (
        temp.groupby("Month")["Close"]
        .agg(["first", "last"])
        .assign(ret=lambda x: (x["last"] / x["first"] - 1) * 100)
        .reset_index()
    )
    monthly["Month_str"] = monthly["Month"].astype(str)
    monthly["Color"] = monthly["ret"].apply(lambda x: _C["up"] if x >= 0 else _C["down"])

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=monthly["Month_str"], y=monthly["ret"],
        marker_color=monthly["Color"], name="Monthly Return",
        text=monthly["ret"].apply(lambda x: f"{x:+.1f}%"),
        textposition="outside",
        textfont=dict(size=11, color=_C["text"]),
    ))
    fig.add_hline(y=0, line_color=_C["text_muted"], line_width=1)
    fig.update_layout(**_layout(
        title=dict(text=f"{ticker} — Monthly Return (%)", font=dict(size=15)),
        xaxis_title="Bulan", yaxis_title="Return (%)",
        height=360, showlegend=False,
    ))
    return fig


def multi_cumulative_return(stocks_df: dict) -> go.Figure:
    fig = go.Figure()
    for i, (ticker, df) in enumerate(stocks_df.items()):
        if df.empty or "Cumulative Return (%)" not in df.columns:
            continue
        fig.add_trace(go.Scatter(
            x=df["Date"], y=df["Cumulative Return (%)"],
            name=ticker.replace(".JK", ""), mode="lines",
            line=dict(color=STOCK_COLORS[i % len(STOCK_COLORS)], width=2),
        ))
    fig.add_hline(y=0, line_dash="dash", line_color=_C["text_muted"], line_width=1)
    fig.update_layout(**_layout(
        title=dict(text="Perbandingan Cumulative Return (%)", font=dict(size=15)),
        yaxis_title="Return (%)", height=420,
        legend=_LEGEND_H,
    ))
    return fig


def multi_price_normalized(stocks_df: dict) -> go.Figure:
    fig = go.Figure()
    for i, (ticker, df) in enumerate(stocks_df.items()):
        if df.empty:
            continue
        normalized = (df["Close"] / df["Close"].iloc[0]) * 100
        fig.add_trace(go.Scatter(
            x=df["Date"], y=normalized,
            name=ticker.replace(".JK", ""), mode="lines",
            line=dict(color=STOCK_COLORS[i % len(STOCK_COLORS)], width=2),
        ))
    fig.add_hline(y=100, line_dash="dot", line_color=_C["text_muted"], line_width=1)
    fig.update_layout(**_layout(
        title=dict(text="Harga Normalisasi (Base = 100)", font=dict(size=15)),
        yaxis_title="Index (Base=100)", height=420,
        legend=_LEGEND_H,
    ))
    return fig


def performance_bar_chart(summary_df: pd.DataFrame) -> go.Figure:
    df = summary_df.sort_values("YTD Return (%)")
    colors = [_C["up"] if v >= 0 else _C["down"] for v in df["YTD Return (%)"]]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["YTD Return (%)"], y=df["Ticker"],
        orientation="h", marker_color=colors,
        text=df["YTD Return (%)"].apply(lambda x: f"{x:+.2f}%"),
        textposition="outside",
        textfont=dict(size=11),
    ))
    fig.add_vline(x=0, line_color=_C["text_muted"], line_width=1)
    fig.update_layout(**_layout(
        title=dict(text="YTD Return per Saham (%)", font=dict(size=15)),
        xaxis_title="Return (%)",
        height=420, showlegend=False,
        margin=dict(l=90, r=80, t=48, b=40),
    ))
    return fig


def volatility_comparison_bar(summary_df: pd.DataFrame) -> go.Figure:
    df = summary_df.sort_values("Volatility (%)", ascending=False)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["Ticker"], y=df["Volatility (%)"],
        marker=dict(
            color=df["Volatility (%)"],
            colorscale=[[0, "#6C63FF"], [0.5, "#4A90D9"], [1, "#EF4444"]],
            showscale=False,
        ),
        text=df["Volatility (%)"].apply(lambda x: f"{x:.1f}%"),
        textposition="outside",
        textfont=dict(size=11),
    ))
    fig.update_layout(**_layout(
        title=dict(text="Volatilitas Tahunan per Saham (%)", font=dict(size=15)),
        yaxis_title="Annualised Volatility (%)",
        height=380, showlegend=False,
    ))
    return fig


def correlation_heatmap(price_matrix: pd.DataFrame) -> go.Figure:
    corr = price_matrix.pct_change().dropna().corr()
    labels = [t.replace(".JK", "") for t in corr.columns]
    fig = go.Figure(go.Heatmap(
        z=corr.values,
        x=labels, y=labels,
        colorscale=[[0.0, "#EF4444"], [0.5, "#F5F6FA"], [1.0, "#6C63FF"]],
        zmin=-1, zmax=1,
        text=[[f"{v:.2f}" for v in row] for row in corr.values],
        texttemplate="%{text}",
        textfont=dict(size=11),
        colorbar=dict(title="Correlation"),
    ))
    fig.update_layout(**_layout(
        title=dict(text="Matriks Korelasi Daily Return", font=dict(size=15)),
        height=420,
        margin=dict(l=60, r=20, t=48, b=60),
    ))
    return fig


def sector_performance_chart(summary_df: pd.DataFrame) -> go.Figure:
    sector_avg = (
        summary_df.groupby("Sector")["YTD Return (%)"]
        .mean()
        .reset_index()
        .sort_values("YTD Return (%)")
    )
    colors = [_C["up"] if v >= 0 else _C["down"] for v in sector_avg["YTD Return (%)"]]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=sector_avg["YTD Return (%)"], y=sector_avg["Sector"],
        orientation="h", marker_color=colors,
        text=sector_avg["YTD Return (%)"].apply(lambda x: f"{x:+.2f}%"),
        textposition="outside",
        textfont=dict(size=12),
    ))
    fig.add_vline(x=0, line_color=_C["text_muted"], line_width=1)
    fig.update_layout(**_layout(
        title=dict(text="Rata-rata Return per Sektor (%)", font=dict(size=15)),
        xaxis_title="Avg Return (%)",
        height=300, showlegend=False,
        margin=dict(l=130, r=80, t=48, b=40),
    ))
    return fig
