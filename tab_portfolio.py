"""tab_portfolio.py — Portfolio VaR / CVaR / ES with weights"""
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from scipy.stats import norm

from components import (section_h, render_card, ib, render_ib, fml, bdg,
                        metric_card, table_html, four_col, three_col, two_col,
                        five_col, NO_SEL, FH, FB, FM, TXT, hl, gt, rt, lb, mut, p,
                        var_result_card)
from var_engine import (all_var_methods, portfolio_parametric_var, component_var,
                        incremental_var, diversification_benefit, mc_portfolio_var,
                        extended_shortfall_metrics, descriptive_stats,
                        portfolio_returns, scale_var, rolling_var)

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(13,31,58,0.6)",
    font=dict(family="Source Sans Pro", color="#e6f1ff"),
    xaxis=dict(gridcolor="#1e3a5f", showgrid=True, zeroline=False),
    yaxis=dict(gridcolor="#1e3a5f", showgrid=True, zeroline=False),
    legend=dict(bgcolor="rgba(17,34,64,0.9)", bordercolor="#1e3a5f", borderwidth=1),
    margin=dict(l=20, r=20, t=50, b=20),
)

COLORS = ["#FFD700","#ADD8E6","#28a745","#ff9f43","#a29bfe","#64ffda",
          "#dc3545","#00cec9","#fd79a8","#e17055","#74b9ff","#55efc4"]


def tab_portfolio(prices_df: pd.DataFrame, selected_tickers: list,
                  weights: list, conf_level: float, horizon: int,
                  n_sims: int, invest: float, ret_method: str):
    """Portfolio VaR analysis."""

    if prices_df is None or len(selected_tickers) < 2:
        st.warning("⚠️ Select at least 2 stocks for portfolio analysis.")
        return

    # Align columns
    available = [t for t in selected_tickers if t in prices_df.columns]
    if len(available) < 2:
        st.error("Not enough data for selected tickers.")
        return

    px_df   = prices_df[available].dropna()
    if len(px_df) < 30:
        st.error("Insufficient price history for portfolio analysis.")
        return

    if ret_method == "Log Returns":
        ret_df = np.log(px_df / px_df.shift(1)).dropna()
    else:
        ret_df = px_df.pct_change().dropna()

    w_raw   = np.array(weights[:len(available)], dtype=float)
    w       = w_raw / w_raw.sum()
    port_r  = portfolio_returns(ret_df, w)

    # ── Portfolio summary header ──────────────────────────────────
    tickers_str = " · ".join([f"{t} ({w_raw[i]:.0f}%)" for i, t in enumerate(available)])
    st.html(
        f'<div style="background:linear-gradient(135deg,#003366,#004d80);'
        f'border-radius:12px;padding:20px 24px;margin-bottom:16px;{NO_SEL}">'
        f'<span style="font-family:{FH};color:#FFD700;-webkit-text-fill-color:#FFD700;'
        f'font-size:1.4rem;font-weight:700">Portfolio Analysis</span><br>'
        f'<span style="color:#ADD8E6;-webkit-text-fill-color:#ADD8E6;'
        f'font-family:{FB};font-size:.85rem">{tickers_str}</span><br>'
        f'<span style="color:#8892b0;-webkit-text-fill-color:#8892b0;'
        f'font-family:{FB};font-size:.80rem">'
        f'Confidence: {conf_level*100:.0f}% | Horizon: {horizon}d | Investment: ₹{invest:,.0f}'
        f'</span></div>'
    )

    # Compute all metrics
    param   = portfolio_parametric_var(ret_df, w, conf_level)
    mc_res  = mc_portfolio_var(ret_df, w, conf_level, n_sims)
    hist_r  = all_var_methods(port_r, conf_level, n_sims)
    ext     = extended_shortfall_metrics(port_r, conf_level)
    div     = diversification_benefit(ret_df, w, conf_level)
    comp_df = component_var(ret_df, w, conf_level)
    incr_df = incremental_var(ret_df, w, conf_level)
    port_stats = descriptive_stats(port_r, "Portfolio")

    # ── Summary metrics ───────────────────────────────────────────
    m1 = metric_card("Hist VaR (1-Day)",    f"{hist_r['Historical']['var']*100:.3f}%",
                     f"₹{hist_r['Historical']['var']*invest:,.0f}", "#dc3545")
    m2 = metric_card("Hist CVaR",           f"{hist_r['Historical']['cvar']*100:.3f}%",
                     f"₹{hist_r['Historical']['cvar']*invest:,.0f}", "#ff9f43")
    m3 = metric_card("Parametric VaR",      f"{param['var']*100:.3f}%",
                     f"₹{param['var']*invest:,.0f}", "#FFD700")
    m4 = metric_card("MC VaR",              f"{mc_res['var']*100:.3f}%",
                     f"₹{mc_res['var']*invest:,.0f}", "#a29bfe")
    m5 = metric_card("Portfolio Volatility",f"{param['port_vol']*100*np.sqrt(252):.2f}%",
                     f"Daily σ: {param['port_vol']*100:.3f}%", "#ADD8E6")
    m6 = metric_card("Diversification",     f"{div['diversification_benefit']*100:.3f}%",
                     f"Ratio: {div['diversification_ratio']:.3f}x", "#64ffda")
    st.html(f'<div style="display:grid;grid-template-columns:repeat(6,1fr);gap:9px;margin-bottom:14px">'
            + "".join(f'<div>{m}</div>' for m in [m1,m2,m3,m4,m5,m6]) + '</div>')

    # ── Multi-method VaR comparison ───────────────────────────────
    section_h("📐 All VaR Methods — Portfolio")
    icons = {"Historical":"📊","Normal":"📈","Student-t":"📉",
             "Cornish-Fisher":"🌀","Monte Carlo":"🎲","EWMA":"⚡","GARCH(1,1)":"🔥"}
    colors_map = {
        "Historical":"#ADD8E6","Normal":"#FFD700","Student-t":"#64ffda",
        "Cornish-Fisher":"#ff9f43","Monte Carlo":"#a29bfe","EWMA":"#28a745","GARCH(1,1)":"#dc3545"
    }
    cols_v = st.columns(7)
    for i, (k, res) in enumerate(hist_r.items()):
        with cols_v[i]:
            st.html(var_result_card(icons.get(k,"📐")+" "+k,
                                    f"{res['var']*100:.3f}%",
                                    f"{res['cvar']*100:.3f}%",
                                    colors_map.get(k,"#FFD700")))

    # ── Portfolio return distribution ─────────────────────────────
    section_h("📉 Portfolio Return Distribution")
    c1, c2 = st.columns([2, 1])
    with c1:
        fig = go.Figure()
        fig.add_trace(go.Histogram(x=port_r * 100, nbinsx=80,
                                   marker_color="#004d80", opacity=0.75, name="Portfolio Returns"))
        # VaR lines
        var_lines = [
            ("Hist VaR",  hist_r["Historical"]["var"],  "#FFD700"),
            ("Norm VaR",  hist_r["Normal"]["var"],       "#ADD8E6"),
            ("MC VaR",    mc_res["var"],                 "#a29bfe"),
            ("Hist CVaR", hist_r["Historical"]["cvar"],  "#ff9f43"),
        ]
        for name, val, col in var_lines:
            fig.add_vline(x=-val*100, line_dash="dash", line_color=col, line_width=2,
                          annotation_text=name, annotation_font_color=col,
                          annotation_font_size=9)
        fig.update_layout(**PLOTLY_LAYOUT, height=360,
                          title="Portfolio Daily Return Distribution",
                          xaxis_title="Return (%)", yaxis_title="Frequency")
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        # Correlation heatmap
        corr = ret_df.corr()
        fig_corr = px.imshow(corr, color_continuous_scale=[[0,"#003366"],[0.5,"#FFD700"],[1,"#dc3545"]],
                             text_auto=".2f", aspect="auto",
                             title="Return Correlation Matrix")
        fig_corr.update_layout(**PLOTLY_LAYOUT, height=360,
                               coloraxis_showscale=False)
        fig_corr.update_traces(textfont_size=10)
        st.plotly_chart(fig_corr, use_container_width=True)

    # ── Multi-horizon ─────────────────────────────────────────────
    section_h(f"📅 Multi-Horizon Portfolio VaR — Investment ₹{invest:,.0f}")
    hist_var_1d = hist_r["Historical"]["var"]
    norm_var_1d = hist_r["Normal"]["var"]
    horizons = [1, 2, 5, 10, 21, 63, 252]
    rows_h = []
    for h in horizons:
        hv = scale_var(hist_var_1d, h)
        nv = scale_var(norm_var_1d, h)
        rows_h.append([
            f"{h}d", f"{hv*100:.3f}%", f"₹{hv*invest:,.0f}",
            f"{nv*100:.3f}%", f"₹{nv*invest:,.0f}",
        ])
    st.html(table_html(
        ["Horizon", "Hist VaR %", "Hist VaR ₹", "Normal VaR %", "Normal VaR ₹"], rows_h
    ))

    # ── Component VaR ─────────────────────────────────────────────
    section_h("🧩 Component VaR — Attribution")
    c3, c4 = st.columns([1, 1])
    with c3:
        rows_c = []
        for _, row in comp_df.iterrows():
            rows_c.append([
                row["Ticker"],
                f"{row['Weight (%)']:.1f}%",
                f"{row['Marginal VaR']:.5f}",
                f"{row['Component VaR']:.5f}",
                f"{row['% Contribution']:.1f}%",
            ])
        st.html(table_html(["Ticker","Weight","Marginal VaR","Component VaR","% Contrib"], rows_c))

    with c4:
        fig_comp = go.Figure(go.Bar(
            x=comp_df["Ticker"], y=comp_df["% Contribution"],
            marker_color=COLORS[:len(comp_df)],
            text=[f"{v:.1f}%" for v in comp_df["% Contribution"]],
            textposition="outside", textfont=dict(color="#e6f1ff", size=10)
        ))
        fig_comp.update_layout(**PLOTLY_LAYOUT, height=300,
                               title="VaR Contribution by Stock",
                               yaxis_title="% Contribution to Portfolio VaR")
        st.plotly_chart(fig_comp, use_container_width=True)

    # ── Incremental VaR ───────────────────────────────────────────
    section_h("➕ Incremental VaR — Impact of Removing Each Position")
    c5, c6 = st.columns([1, 1])
    with c5:
        rows_i = []
        for _, row in incr_df.iterrows():
            sign = "+" if row["Incremental VaR"] > 0 else ""
            color = "#dc3545" if row["Incremental VaR"] > 0 else "#28a745"
            rows_i.append([
                row["Ticker"],
                f'<span style="color:{color};-webkit-text-fill-color:{color}">'
                f'{sign}{row["Incremental VaR"]:.5f}</span>',
                f'{sign}{row["% of Portfolio VaR"]:.2f}%',
            ])
        st.html(table_html(["Ticker","Incremental VaR","% Change in Port VaR"], rows_i))

    with c6:
        inc_colors = ["#dc3545" if v > 0 else "#28a745" for v in incr_df["Incremental VaR"]]
        fig_inc = go.Figure(go.Bar(
            x=incr_df["Ticker"], y=incr_df["Incremental VaR"] * 100,
            marker_color=inc_colors,
            text=[f"{v*100:.4f}%" for v in incr_df["Incremental VaR"]],
            textposition="outside", textfont=dict(color="#e6f1ff", size=9)
        ))
        fig_inc.update_layout(**PLOTLY_LAYOUT, height=300,
                               title="Incremental VaR (Positive = Risk Increasing)",
                               yaxis_title="Incremental VaR (%)")
        st.plotly_chart(fig_inc, use_container_width=True)

    # ── Diversification benefit ───────────────────────────────────
    section_h("🌐 Diversification Benefit")
    d1 = metric_card("Undiversified VaR", f"{div['undiversified_var']*100:.3f}%",
                     "Sum of individual VaRs", "#ff9f43")
    d2 = metric_card("Portfolio VaR",     f"{div['portfolio_var']*100:.3f}%",
                     "After diversification", "#28a745")
    d3 = metric_card("Diversification Benefit", f"{div['diversification_benefit']*100:.3f}%",
                     "Risk reduction", "#64ffda")
    d4 = metric_card("Diversification Ratio", f"{div['diversification_ratio']:.3f}x",
                     ">1.0 = diversified", "#FFD700")
    st.html(f'<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:14px">'
            f'<div>{d1}</div><div>{d2}</div><div>{d3}</div><div>{d4}</div></div>')

    # Stacked bar chart: undiversified vs diversified
    fig_div = go.Figure()
    fig_div.add_trace(go.Bar(
        name="Individual VaRs",
        x=available,
        y=[(norm.ppf(conf_level) * ret_df[t].std()) * 100 for t in available],
        marker_color=COLORS[:len(available)],
    ))
    fig_div.add_trace(go.Bar(
        name="After Portfolio",
        x=["PORTFOLIO"],
        y=[div["portfolio_var"] * 100],
        marker_color="#28a745",
    ))
    fig_div.add_hline(y=div["undiversified_var"] * 100,
                      line_dash="dash", line_color="#FFD700",
                      annotation_text="Undiversified Sum")
    fig_div.update_layout(**PLOTLY_LAYOUT, height=340,
                           title="Individual VaRs vs Portfolio VaR (Diversification)",
                           yaxis_title="VaR (%)")
    st.plotly_chart(fig_div, use_container_width=True)

    # ── Extended Shortfall ────────────────────────────────────────
    section_h("🎯 Extended Shortfall — Portfolio")
    em = ext
    e1 = metric_card("Expected Shortfall",    f"{em['es']*100:.3f}%",           "≡ CVaR Historical",       "#ff9f43")
    e2 = metric_card("Stressed ES",           f"{em['stressed_es']*100:.3f}%",  "Worst 60-day window",     "#dc3545")
    e3 = metric_card("Spectral Risk Measure", f"{em['spectral_rm']*100:.3f}%",  "Exp-weighted tail",       "#a29bfe")
    e4 = metric_card("Entropic VaR",          f"{em['evar']*100:.3f}%",         "Upper bound to ES",       "#64ffda")
    e5 = metric_card("Range VaR",             f"{em['range_var']*100:.3f}%",    "VaR(99%) - VaR(95%)",     "#FFD700")
    st.html(f'<div style="display:grid;grid-template-columns:repeat(5,1fr);gap:10px;margin-bottom:14px">'
            + "".join(f'<div>{e}</div>' for e in [e1,e2,e3,e4,e5]) + '</div>')

    # ── Monte Carlo simulation fan ────────────────────────────────
    section_h("🎲 Monte Carlo Portfolio Simulation")
    n_paths = 200
    port_mu   = port_r.mean()
    port_sig  = port_r.std()
    sim_paths = np.zeros((n_paths, horizon))
    for i in range(n_paths):
        daily_r = np.random.normal(port_mu, port_sig, horizon)
        sim_paths[i] = np.cumprod(1 + daily_r) - 1

    fig_mc = go.Figure()
    for i in range(n_paths):
        color = "#dc3545" if sim_paths[i, -1] < -mc_res["var"] else "#1e4a7a"
        fig_mc.add_trace(go.Scatter(
            x=list(range(1, horizon + 1)), y=sim_paths[i] * 100,
            mode="lines", line=dict(color=color, width=0.6),
            showlegend=False, opacity=0.4
        ))
    # Median and percentile bands
    p50 = np.percentile(sim_paths, 50, axis=0) * 100
    p5  = np.percentile(sim_paths, 5,  axis=0) * 100
    p1  = np.percentile(sim_paths, 1,  axis=0) * 100
    fig_mc.add_trace(go.Scatter(x=list(range(1, horizon+1)), y=p50,
                                mode="lines", name="Median",
                                line=dict(color="#FFD700", width=2.5)))
    fig_mc.add_trace(go.Scatter(x=list(range(1, horizon+1)), y=p5,
                                mode="lines", name="5th Pct (VaR)",
                                line=dict(color="#ff9f43", width=2, dash="dash")))
    fig_mc.add_trace(go.Scatter(x=list(range(1, horizon+1)), y=p1,
                                mode="lines", name="1st Pct",
                                line=dict(color="#dc3545", width=2, dash="dot")))
    fig_mc.update_layout(**PLOTLY_LAYOUT, height=380,
                          title=f"Monte Carlo — {n_paths} Portfolio Paths over {horizon} Days",
                          xaxis_title="Trading Days", yaxis_title="Cumulative Return (%)")
    st.plotly_chart(fig_mc, use_container_width=True)

    # ── Efficient Frontier (optional if ≥3 stocks) ────────────────
    if len(available) >= 3:
        section_h("📈 Risk-Return Efficient Frontier")
        n_portfolios = 2000
        mus     = ret_df.mean().values
        cov_mat = ret_df.cov().values
        port_vols, port_rets, port_sharpes = [], [], []
        for _ in range(n_portfolios):
            rw = np.random.dirichlet(np.ones(len(available)))
            pv = np.sqrt(rw @ cov_mat @ rw)
            pr = rw @ mus
            port_vols.append(pv * np.sqrt(252) * 100)
            port_rets.append(pr * 252 * 100)
            port_sharpes.append(pr / pv if pv > 0 else 0)
        fig_ef = go.Figure()
        fig_ef.add_trace(go.Scatter(
            x=port_vols, y=port_rets, mode="markers",
            marker=dict(color=port_sharpes, colorscale="Viridis", size=4,
                        colorbar=dict(title="Sharpe"), opacity=0.7),
            name="Random Portfolios"
        ))
        # Current portfolio
        cur_vol = param["port_vol"] * np.sqrt(252) * 100
        cur_ret = port_r.mean() * 252 * 100
        fig_ef.add_trace(go.Scatter(x=[cur_vol], y=[cur_ret], mode="markers",
                                    marker=dict(color="#FFD700", size=16, symbol="star"),
                                    name="Current Portfolio"))
        fig_ef.update_layout(**PLOTLY_LAYOUT, height=380,
                              title="Monte Carlo Efficient Frontier",
                              xaxis_title="Annual Volatility (%)",
                              yaxis_title="Annual Return (%)")
        st.plotly_chart(fig_ef, use_container_width=True)

    # ── Portfolio stats ───────────────────────────────────────────
    section_h("📋 Portfolio Statistics")
    st.html(table_html(
        ["Statistic", "Value"],
        [
            ["Mean Daily Return",       f"{port_stats['mean_daily']*100:.4f}%"],
            ["Mean Annual Return",      f"{port_stats['mean_annual']*100:.2f}%"],
            ["Daily Volatility",        f"{port_stats['vol_daily']*100:.4f}%"],
            ["Annual Volatility",       f"{port_stats['vol_annual']*100:.2f}%"],
            ["Portfolio Skewness",      f"{port_stats['skewness']:.4f}"],
            ["Portfolio Excess Kurtosis",f"{port_stats['excess_kurt']:.4f}"],
            ["Sharpe Ratio",            f"{port_stats['sharpe']:.4f}"],
            ["Maximum Drawdown",        f"{port_stats['max_drawdown']*100:.2f}%"],
            ["Observations",            str(port_stats["n_obs"])],
        ]
    ))

    # ── Formulas ──────────────────────────────────────────────────
    section_h("📚 Portfolio VaR Formulae")
    st.html(fml(
        "Portfolio Return:     r_p = Σ w_i · r_i\n"
        "Portfolio Variance:   σ²_p = w' Σ w   (Σ = covariance matrix)\n"
        "Parametric VaR:       VaR_p = -(μ_p + z_α · σ_p)\n"
        "Parametric CVaR:      CVaR_p = -(μ_p - σ_p · φ(z_α) / α)\n\n"
        "Marginal VaR_i:       = (Σ w)_i / σ_p · z_α\n"
        "Component VaR_i:      = w_i · Marginal VaR_i\n"
        "Σ Component VaR_i:    = Portfolio VaR\n\n"
        "Diversification Ratio = Undiversified VaR / Portfolio VaR\n"
        "Div Benefit           = Σ(w_i · VaR_i) - VaR_portfolio\n\n"
        "MC VaR:               Cholesky L: Σ = L·L' → sim = z·L' + μ, z~N(0,I)"
    ))
