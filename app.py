"""
app.py — Nifty 50 VaR / CVaR / ES Risk Dashboard
The Mountain Path — World of Finance
Prof. V. Ravichandran

Tabs:
  1. Single Stock VaR
  2. Portfolio VaR
  3. Stress Testing
  4. Methodology
"""
import streamlit as st
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings("ignore")

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Nifty VaR / CVaR / ES Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

from styles     import inject_css
from components import hero_header, footer, section_h, render_ib, hl, bdg, NO_SEL, FH, FB
from var_engine import NIFTY50, SECTOR_MAP, fetch_data, compute_returns

inject_css()

# ── Hero header ───────────────────────────────────────────────────────────────
hero_header(
    "Nifty 50 VaR / CVaR / ES Risk Dashboard",
    "Live market risk analytics — Historical · Parametric · Monte Carlo · EWMA · GARCH(1,1) · Cornish-Fisher | "
    "Single Stock & Portfolio | Stress Testing | Basel III / FRTB Reference",
    "📊"
)

# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(
        f'<div style="background:#003366;border-radius:10px;padding:16px;'
        f'margin-bottom:12px;text-align:center;user-select:none">'
        f'<div style="font-family:{FH};color:#FFD700;-webkit-text-fill-color:#FFD700;'
        f'font-size:1.15rem;font-weight:700">⚙️ Control Panel</div>'
        f'<div style="color:#8892b0;-webkit-text-fill-color:#8892b0;'
        f'font-family:{FB};font-size:.78rem;margin-top:4px">'
        f'The Mountain Path — World of Finance</div>'
        f'</div>',
        unsafe_allow_html=True
    )

    # ── Data Parameters ───────────────────────────────────────────
    st.markdown(
        f'<div style="color:#ADD8E6;-webkit-text-fill-color:#ADD8E6;'
        f'font-family:{FB};font-weight:700;font-size:.85rem;margin-bottom:4px">'
        f'📦 Data Parameters</div>',
        unsafe_allow_html=True
    )
    period = st.selectbox("Data Period", ["1y","2y","3y","5y","6mo","3mo"],
                          help="Historical price data window for VaR estimation")
    ret_method = st.radio("Return Method", ["Log Returns","Simple Returns"],
                          help="Log returns preferred for VaR analysis")

    st.markdown("<hr style='border-color:#1e3a5f;margin:10px 0'>", unsafe_allow_html=True)

    # ── VaR Parameters ────────────────────────────────────────────
    st.markdown(
        f'<div style="color:#ADD8E6;-webkit-text-fill-color:#ADD8E6;'
        f'font-family:{FB};font-weight:700;font-size:.85rem;margin-bottom:4px">'
        f'📐 VaR Parameters</div>',
        unsafe_allow_html=True
    )
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
    invest  = st.number_input("Portfolio Value (₹)", value=1000000, step=100000,
                               min_value=10000, format="%d",
                               help="Investment amount for ₹ loss calculation")

    st.markdown("<hr style='border-color:#1e3a5f;margin:10px 0'>", unsafe_allow_html=True)

    # ── Stock Selection ───────────────────────────────────────────
    st.markdown(
        f'<div style="color:#ADD8E6;-webkit-text-fill-color:#ADD8E6;'
        f'font-family:{FB};font-weight:700;font-size:.85rem;margin-bottom:4px">'
        f'🏦 Nifty 50 Stocks</div>',
        unsafe_allow_html=True
    )

    # Sector filter
    all_sectors = sorted(set(SECTOR_MAP.values()))
    sel_sectors = st.multiselect("Filter by Sector", all_sectors,
                                  default=all_sectors[:3],
                                  help="Filter stock list by sector")
    filtered_tickers = [k for k, v in SECTOR_MAP.items() if v in sel_sectors] if sel_sectors else list(NIFTY50.keys())

    # Single stock (for Tab 1)
    single_ticker = st.selectbox(
        "Single Stock Analysis",
        filtered_tickers,
        format_func=lambda x: f"{x} ({SECTOR_MAP.get(x,'—')})",
        help="Select stock for Tab 1"
    )

    # Portfolio stocks (for Tab 2)
    st.markdown(
        f'<div style="color:#ADD8E6;-webkit-text-fill-color:#ADD8E6;'
        f'font-family:{FB};font-weight:700;font-size:.82rem;margin:8px 0 4px">'
        f'📂 Portfolio Stocks (Tab 2)</div>',
        unsafe_allow_html=True
    )
    default_port = filtered_tickers[:min(5, len(filtered_tickers))]
    portfolio_tickers = st.multiselect(
        "Select Stocks",
        list(NIFTY50.keys()),
        default=default_port,
        format_func=lambda x: f"{x} ({SECTOR_MAP.get(x,'—')})",
        help="Select 2–12 stocks for portfolio VaR"
    )

    # ── Portfolio Weights ─────────────────────────────────────────
    weights = []
    if portfolio_tickers:
        st.markdown(
            f'<div style="color:#ADD8E6;-webkit-text-fill-color:#ADD8E6;'
            f'font-family:{FB};font-weight:700;font-size:.82rem;margin:8px 0 4px">'
            f'⚖️ Portfolio Weights (%)</div>',
            unsafe_allow_html=True
        )
        equal_w = round(100 / len(portfolio_tickers), 1)
        for ticker in portfolio_tickers:
            w = st.number_input(
                f"{ticker}", value=equal_w, min_value=0.0, max_value=100.0,
                step=5.0, format="%.1f", key=f"w_{ticker}"
            )
            weights.append(w)
        total_w = sum(weights)
        w_color = "#28a745" if abs(total_w - 100) < 0.1 else "#dc3545"
        st.markdown(
            f'<div style="color:{w_color};-webkit-text-fill-color:{w_color};'
            f'font-family:{FB};font-size:.82rem;font-weight:700;margin-top:6px">'
            f'Total: {total_w:.1f}% (auto-normalised)</div>',
            unsafe_allow_html=True
        )

    st.markdown("<hr style='border-color:#1e3a5f;margin:10px 0'>", unsafe_allow_html=True)

    # ── Fetch button ──────────────────────────────────────────────
    fetch_btn = st.button("🔄 Fetch Live Data", use_container_width=True)

    st.markdown(
        f'<div style="color:#8892b0;-webkit-text-fill-color:#8892b0;'
        f'font-family:{FB};font-size:.74rem;margin-top:8px;text-align:center">'
        f'Data: NSE via Yahoo Finance | Live prices delayed ~15min</div>',
        unsafe_allow_html=True
    )

# ═══════════════════════════════════════════════════════════════════════════════
# DATA LOADING
# ═══════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=900, show_spinner=False)  # cache 15 min
def load_prices(tickers_list: tuple, period: str) -> pd.DataFrame:
    """Cache-aware data loader."""
    ticker_symbols = [NIFTY50[t] for t in tickers_list if t in NIFTY50]
    return fetch_data(ticker_symbols, period)


def remap_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Remap .NS suffixed columns back to short ticker names."""
    reverse = {v: k for k, v in NIFTY50.items()}
    df.columns = [reverse.get(c, c) for c in df.columns]
    return df


# Determine all tickers needed
all_tickers_needed = list(set(
    [single_ticker] + (portfolio_tickers if portfolio_tickers else [])
))

prices_df = None
if fetch_btn or "prices_df" in st.session_state:
    if fetch_btn:
        with st.spinner("⏳ Fetching live Nifty 50 data from NSE via Yahoo Finance..."):
            try:
                tickers_key = tuple(sorted(all_tickers_needed))
                raw = load_prices(tickers_key, period)
                if raw is not None and len(raw) > 5:
                    prices_df = remap_columns(raw)
                    st.session_state["prices_df"] = prices_df
                    st.session_state["last_period"] = period
                    st.success(f"✅ Data loaded: {len(prices_df)} trading days | "
                               f"{len(prices_df.columns)} stocks | "
                               f"Latest: {prices_df.index[-1].date()}")
                else:
                    st.error("❌ Failed to fetch data. Please check your internet connection.")
            except Exception as e:
                st.error(f"❌ Data fetch error: {e}")
    else:
        prices_df = st.session_state.get("prices_df")

if prices_df is None:
    st.info(
        "👆 **Click 'Fetch Live Data'** to download Nifty 50 stock prices from NSE via Yahoo Finance.\n\n"
        "This app computes:\n"
        "- **7 VaR Methods**: Historical, Parametric (Normal), Student-t, Cornish-Fisher, Monte Carlo, EWMA, GARCH(1,1)\n"
        "- **CVaR / Expected Shortfall** for each method\n"
        "- **Extended ES Metrics**: Spectral RM, Entropic VaR, Stressed ES, Range VaR\n"
        "- **Portfolio Risk**: Component VaR, Marginal VaR, Incremental VaR, Diversification Benefit\n"
        "- **Stress Testing**: Historical crisis scenarios (COVID-19, GFC 2008, IL&FS, etc.)\n"
        "- **Backtesting**: Kupiec POF test"
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

tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Single Stock VaR",
    "💼 Portfolio VaR",
    "🔥 Stress Testing",
    "📚 Methodology",
])

with tab1:
    tab_single(
        prices_df   = prices_df,
        ticker      = single_ticker,
        conf_level  = conf_level,
        horizon     = horizon,
        n_sims      = n_sims,
        invest      = invest,
        ret_method  = ret_method,
    )

with tab2:
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

with tab3:
    tab_stress(
        prices_df        = prices_df,
        selected_tickers = portfolio_tickers if portfolio_tickers else [single_ticker],
        weights          = weights if weights else [1.0],
        ret_method       = ret_method,
    )

with tab4:
    tab_methodology()

footer()
