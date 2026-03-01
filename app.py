"""
app.py — Nifty 50 VaR / CVaR / ES Risk Dashboard  v2
The Mountain Path — World of Finance | Prof. V. Ravichandran

Redesigned to match Linear Regression app design framework:
  • Centred title hero header with badge strip
  • Styled tabs with gold active state
  • Enhanced sidebar with section dividers
  • Per-tab banners matching the new colour system
"""
import streamlit as st
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="Nifty 50 VaR / CVaR / ES Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

from styles     import inject_css
from components import (app_header, footer, section_h, render_ib, hl, bdg,
                        NO_SEL, FH, FB, FM)
from var_engine import NIFTY50, SECTOR_MAP, fetch_data, compute_returns

inject_css()

# ── Hero Header (LR app style) ────────────────────────────────────────────────
app_header(
    title    = "Nifty 50 VaR / CVaR / ES Risk Dashboard",
    subtitle = "Live market risk analytics — Historical · Parametric · Monte Carlo · EWMA · GARCH(1,1) · Cornish-Fisher"
               " | Single Stock & Portfolio | Stress Testing | Basel III / FRTB Reference",
    badges   = [
        ("7 VaR Methods",       "blue"),
        ("CVaR / ES",           "gold"),
        ("Monte Carlo",         "purple"),
        ("GARCH(1,1)",          "red"),
        ("Stress Testing",      "amber"),
        ("Basel III / FRTB",    "teal"),
    ]
)

# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    # Brand block
    st.html(
        f'<div style="background:linear-gradient(135deg,#003366,#004d80);border-radius:10px;'
        f'padding:16px;margin-bottom:16px;text-align:center;{NO_SEL}">'
        f'<div style="font-family:{FH};color:#FFD700;-webkit-text-fill-color:#FFD700;'
        f'font-size:1.15rem;font-weight:700">⚙️ Control Panel</div>'
        f'<div style="color:#ADD8E6;-webkit-text-fill-color:#ADD8E6;'
        f'font-family:{FB};font-size:.78rem;margin-top:4px">'
        f'The Mountain Path — World of Finance</div></div>'
    )

    # ── Data Parameters ───────────────────────────────────────────
    st.html(f'<div style="color:#FFD700;-webkit-text-fill-color:#FFD700;font-family:{FB};'
            f'font-weight:700;font-size:.85rem;margin-bottom:6px">📦 Data Parameters</div>')
    period     = st.selectbox("Data Period", ["1y","2y","3y","5y","6mo","3mo"],
                              help="Historical price window for VaR estimation")
    ret_method = st.radio("Return Method", ["Log Returns","Simple Returns"],
                          help="Log returns preferred for VaR analysis")

    st.html("<hr style='border-color:#1e3a5f;margin:12px 0'>")

    # ── VaR Parameters ────────────────────────────────────────────
    st.html(f'<div style="color:#FFD700;-webkit-text-fill-color:#FFD700;font-family:{FB};'
            f'font-weight:700;font-size:.85rem;margin-bottom:6px">📐 VaR Parameters</div>')
    conf_level = st.select_slider(
        "Confidence Level",
        options=[0.90, 0.95, 0.975, 0.99, 0.999],
        value=0.95,
        format_func=lambda x: f"{x*100:.1f}%"
    )
    horizon = st.slider("VaR Horizon (days)", 1, 252, 1,
                        help="1-day for trading, 10-day for Basel, 252-day for annual")
    n_sims  = st.select_slider("MC Simulations",
                                options=[10000, 25000, 50000, 100000],
                                value=50000,
                                format_func=lambda x: f"{x:,}")
    invest  = st.number_input("Portfolio Value (₹)", value=1_000_000, step=100_000,
                               min_value=10_000, format="%d",
                               help="Investment amount for ₹ loss calculation")

    st.html("<hr style='border-color:#1e3a5f;margin:12px 0'>")

    # ── Stock Selection ───────────────────────────────────────────
    st.html(f'<div style="color:#FFD700;-webkit-text-fill-color:#FFD700;font-family:{FB};'
            f'font-weight:700;font-size:.85rem;margin-bottom:6px">🏦 Nifty 50 Stocks</div>')
    all_sectors  = sorted(set(SECTOR_MAP.values()))
    sel_sectors  = st.multiselect("Filter by Sector", all_sectors, default=all_sectors[:3])
    filtered     = [k for k, v in SECTOR_MAP.items() if v in sel_sectors] if sel_sectors else list(NIFTY50.keys())

    single_ticker = st.selectbox(
        "Single Stock Analysis",
        filtered,
        format_func=lambda x: f"{x} ({SECTOR_MAP.get(x,'—')})"
    )

    st.html(f'<div style="color:#ADD8E6;-webkit-text-fill-color:#ADD8E6;font-family:{FB};'
            f'font-weight:700;font-size:.82rem;margin:10px 0 4px">📂 Portfolio Stocks</div>')
    default_port     = filtered[:min(5, len(filtered))]
    portfolio_tickers = st.multiselect(
        "Select Stocks",
        list(NIFTY50.keys()),
        default=default_port,
        format_func=lambda x: f"{x} ({SECTOR_MAP.get(x,'—')})"
    )

    # Weights
    weights = []
    if portfolio_tickers:
        st.html(f'<div style="color:#ADD8E6;-webkit-text-fill-color:#ADD8E6;font-family:{FB};'
                f'font-weight:700;font-size:.82rem;margin:10px 0 4px">⚖️ Weights (%)</div>')
        equal_w = round(100 / len(portfolio_tickers), 1)
        for ticker in portfolio_tickers:
            w = st.number_input(
                f"{ticker}", value=equal_w, min_value=0.0, max_value=100.0,
                step=5.0, format="%.1f", key=f"w_{ticker}"
            )
            weights.append(w)
        total_w = sum(weights)
        w_color = "#28a745" if abs(total_w - 100) < 0.1 else "#dc3545"
        st.html(
            f'<div style="color:{w_color};-webkit-text-fill-color:{w_color};'
            f'font-family:{FB};font-size:.82rem;font-weight:700;margin-top:6px">'
            f'Total: {total_w:.1f}%  (auto-normalised)</div>'
        )

    st.html("<hr style='border-color:#1e3a5f;margin:12px 0'>")
    fetch_btn = st.button("🔄 Fetch Live Data", use_container_width=True)
    st.html(
        f'<div style="color:#8892b0;-webkit-text-fill-color:#8892b0;font-family:{FB};'
        f'font-size:.74rem;margin-top:8px;text-align:center">'
        f'NSE via Yahoo Finance · Prices delayed ~15 min</div>'
    )

# ═══════════════════════════════════════════════════════════════════════════════
# DATA LOADING
# ═══════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=900, show_spinner=False)
def load_prices(tickers_list: tuple, period: str) -> pd.DataFrame:
    ticker_symbols = [NIFTY50[t] for t in tickers_list if t in NIFTY50]
    return fetch_data(ticker_symbols, period)

def remap_columns(df: pd.DataFrame) -> pd.DataFrame:
    reverse = {v: k for k, v in NIFTY50.items()}
    df.columns = [reverse.get(c, c) for c in df.columns]
    return df

all_tickers_needed = list(set([single_ticker] + (portfolio_tickers or [])))
prices_df = None

if fetch_btn or "prices_df" in st.session_state:
    if fetch_btn:
        with st.spinner("⏳ Fetching live Nifty 50 data from NSE via Yahoo Finance…"):
            try:
                key = tuple(sorted(all_tickers_needed))
                raw = load_prices(key, period)
                if raw is not None and len(raw) > 5:
                    prices_df = remap_columns(raw)
                    st.session_state["prices_df"] = prices_df
                    st.success(
                        f"✅ Data loaded: {len(prices_df)} trading days | "
                        f"{len(prices_df.columns)} stocks | "
                        f"Latest: {prices_df.index[-1].date()}"
                    )
                else:
                    st.error("❌ Failed to fetch data. Check your internet connection.")
            except Exception as e:
                st.error(f"❌ Data fetch error: {e}")
    else:
        prices_df = st.session_state.get("prices_df")

# ── Splash when no data ───────────────────────────────────────────────────────
if prices_df is None:
    st.html(
        f'<div style="background:#112240;border:1px solid #1e3a5f;border-radius:12px;'
        f'padding:36px 40px;text-align:center;margin:20px 0;{NO_SEL}">'
        f'<div style="font-size:3rem;margin-bottom:12px">📊</div>'
        f'<div style="font-family:{FH};color:#FFD700;-webkit-text-fill-color:#FFD700;'
        f'font-size:1.6rem;font-weight:700;margin-bottom:10px">Ready to Analyse Risk</div>'
        f'<div style="color:#ADD8E6;-webkit-text-fill-color:#ADD8E6;font-family:{FB};font-size:.95rem;margin-bottom:20px">'
        f'Click <strong style="color:#FFD700;-webkit-text-fill-color:#FFD700">🔄 Fetch Live Data</strong> '
        f'in the sidebar to load Nifty 50 stock prices from NSE via Yahoo Finance.</div>'
        f'<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:14px;max-width:700px;margin:0 auto">'
        + "".join(
            f'<div style="background:rgba(0,51,102,0.3);border:1px solid #1e3a5f;border-radius:8px;'
            f'padding:14px 10px;{NO_SEL}">'
            f'<div style="font-size:1.5rem;margin-bottom:6px">{icon}</div>'
            f'<div style="color:#FFD700;-webkit-text-fill-color:#FFD700;font-family:{FB};'
            f'font-size:.82rem;font-weight:600">{label}</div>'
            f'<div style="color:#8892b0;-webkit-text-fill-color:#8892b0;font-family:{FB};'
            f'font-size:.75rem;margin-top:3px">{desc}</div></div>'
            for icon, label, desc in [
                ("🎯","7 VaR Methods","Hist · Normal · t · CF · MC · EWMA · GARCH"),
                ("💼","Portfolio Risk","Component, Marginal & Incremental VaR"),
                ("🔥","Stress Testing","COVID-19, GFC 2008 & 6 more scenarios"),
                ("📚","Methodology","Basel III / FRTB formula reference"),
            ]
        )
        + f'</div></div>'
    )
    footer()
    st.stop()

# ═══════════════════════════════════════════════════════════════════════════════
# TABS
# ═══════════════════════════════════════════════════════════════════════════════
from tab_single      import tab_single
from tab_portfolio   import tab_portfolio
from tab_stress      import tab_stress
from tab_methodology import tab_methodology

TABS = st.tabs([
    "📈 Single Stock VaR",
    "💼 Portfolio VaR",
    "🔥 Stress Testing",
    "📚 Methodology",
])

with TABS[0]:
    tab_single(
        prices_df  = prices_df,
        ticker     = single_ticker,
        conf_level = conf_level,
        horizon    = horizon,
        n_sims     = n_sims,
        invest     = invest,
        ret_method = ret_method,
    )

with TABS[1]:
    tab_portfolio(
        prices_df        = prices_df,
        selected_tickers = portfolio_tickers,
        weights          = weights if weights else [1.0] * len(portfolio_tickers),
        conf_level       = conf_level,
        horizon          = horizon,
        n_sims           = n_sims,
        invest           = invest,
        ret_method       = ret_method,
    )

with TABS[2]:
    tab_stress(
        prices_df        = prices_df,
        selected_tickers = portfolio_tickers if portfolio_tickers else [single_ticker],
        weights          = weights if weights else [1.0],
        ret_method       = ret_method,
    )

with TABS[3]:
    tab_methodology()

footer()
