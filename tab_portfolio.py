"""tab_portfolio.py — Portfolio VaR / CVaR / ES  (v2 redesign)"""
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from scipy.stats import norm

from components import (
    section_h, render_card, ib, render_ib, fml, bdg,
    metric_card, hero_metric, table_html,
    four_col, three_col, two_col, five_col, six_col,
    tab_banner, var_result_card,
    NO_SEL, FH, FB, FM, TXT, hl, gt, rt, lb, org, pur, acc, p
)
from var_engine import (
    all_var_methods, portfolio_parametric_var, component_var,
    incremental_var, diversification_benefit, mc_portfolio_var,
    extended_shortfall_metrics, descriptive_stats,
    portfolio_returns, scale_var, rolling_var
)

PL = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(13,31,58,0.55)",
    font=dict(family="Source Sans Pro", color="#e6f1ff"),
    xaxis=dict(gridcolor="#1e3a5f", showgrid=True, zeroline=False),
    yaxis=dict(gridcolor="#1e3a5f", showgrid=True, zeroline=False),
    legend=dict(bgcolor="rgba(17,34,64,0.9)", bordercolor="#1e3a5f", borderwidth=1),
    margin=dict(l=20, r=20, t=50, b=20),
)
COLORS = ["#FFD700","#ADD8E6","#28a745","#ff9f43","#a29bfe","#64ffda",
          "#dc3545","#00cec9","#fd79a8","#e17055","#74b9ff","#55efc4"]


def tab_portfolio(prices_df, selected_tickers, weights, conf_level, horizon,
                  n_sims, invest, ret_method):

    if prices_df is None or len(selected_tickers) < 2:
        render_ib("⚠️ Select at least 2 stocks in the sidebar for portfolio analysis.", "amber")
        return

    available = [t for t in selected_tickers if t in prices_df.columns]
    if len(available) < 2:
        st.error("Not enough data for selected tickers.")
        return

    px_df = prices_df[available].dropna()
    if len(px_df) < 30:
        st.error("Insufficient price history.")
        return

    ret_df = (np.log(px_df / px_df.shift(1)) if ret_method == "Log Returns"
              else px_df.pct_change()).dropna()

    w_raw  = np.array(weights[:len(available)], dtype=float)
    w      = w_raw / w_raw.sum()
    port_r = portfolio_returns(ret_df, w)

    # ── Tab banner ─────────────────────────────────────────────────────────
    tickers_str = " · ".join([f"{t}({w_raw[i]:.0f}%)" for i, t in enumerate(available)])
    tab_banner(
        "💼 Portfolio VaR / CVaR / ES",
        f"{tickers_str}  |  Confidence: {conf_level*100:.0f}%  |  Horizon: {horizon}d  |  ₹{invest:,.0f}"
    )

    # Compute all metrics
    param      = portfolio_parametric_var(ret_df, w, conf_level)
    mc_res     = mc_portfolio_var(ret_df, w, conf_level, n_sims)
    hist_r     = all_var_methods(port_r, conf_level, n_sims)
    ext        = extended_shortfall_metrics(port_r, conf_level)
    div        = diversification_benefit(ret_df, w, conf_level)
    comp_df    = component_var(ret_df, w, conf_level)
    incr_df    = incremental_var(ret_df, w, conf_level)
    port_stats = descriptive_stats(port_r, "Portfolio")

    # ── Hero metrics ────────────────────────────────────────────────────────
    h1 = hero_metric("Hist VaR 1-Day",  f"{hist_r['Historical']['var']*100:.3f}%",
                     f"₹{hist_r['Historical']['var']*invest:,.0f}", "down","#dc3545")
    h2 = hero_metric("Hist CVaR",       f"{hist_r['Historical']['cvar']*100:.3f}%",
                     f"₹{hist_r['Historical']['cvar']*invest:,.0f}","down","#ff9f43")
    h3 = hero_metric("Parametric VaR",  f"{param['var']*100:.3f}%",
                     f"₹{param['var']*invest:,.0f}","down","#FFD700")
    h4 = hero_metric("MC VaR",          f"{mc_res['var']*100:.3f}%",
                     f"₹{mc_res['var']*invest:,.0f}","down","#a29bfe")
    h5 = hero_metric("Port. Volatility",f"{param['port_vol']*100*np.sqrt(252):.2f}%",
                     f"Daily σ {param['port_vol']*100:.3f}%","","#ADD8E6")
    h6 = hero_metric("Diversification", f"{div['diversification_benefit']*100:.3f}%",
                     f"Ratio {div['diversification_ratio']:.3f}x","up","#64ffda")
    st.html('<div style="display:grid;grid-template-columns:repeat(6,1fr);gap:11px;margin-bottom:18px">'
            + "".join(f'<div>{m}</div>' for m in [h1,h2,h3,h4,h5,h6]) + '</div>')

    # ── All 7 VaR methods ───────────────────────────────────────────────────
    section_h("📐 All 7 VaR Methods — Portfolio")
    icons_map = {"Historical":"📊","Normal":"📈","Student-t":"📉",
                 "Cornish-Fisher":"🌀","Monte Carlo":"🎲","EWMA":"⚡","GARCH(1,1)":"🔥"}
    col_map   = {"Historical":"#ADD8E6","Normal":"#FFD700","Student-t":"#64ffda",
                 "Cornish-Fisher":"#ff9f43","Monte Carlo":"#a29bfe","EWMA":"#28a745","GARCH(1,1)":"#dc3545"}
    cards = [var_result_card(f"{icons_map.get(k,'📐')} {k}",
                             f"{r['var']*100:.3f}%", f"{r['cvar']*100:.3f}%",
                             col_map.get(k,"#FFD700"))
             for k, r in hist_r.items()]
    st.html('<div style="display:grid;grid-template-columns:repeat(7,1fr);gap:9px;margin-bottom:14px">'
            + "".join(f'<div>{c}</div>' for c in cards) + '</div>')

    # ── Distribution + Correlation ──────────────────────────────────────────
    section_h("📉 Return Distribution & Correlation Matrix")
    col1, col2 = st.columns([3, 2])
    with col1:
        fig = go.Figure()
        fig.add_trace(go.Histogram(x=port_r*100, nbinsx=80, marker_color="#004d80",
                                   opacity=0.75, name="Portfolio Returns"))
        for name, val, col in [
            ("Hist VaR",  hist_r["Historical"]["var"], "#FFD700"),
            ("Norm VaR",  hist_r["Normal"]["var"],     "#ADD8E6"),
            ("MC VaR",    mc_res["var"],               "#a29bfe"),
            ("Hist CVaR", hist_r["Historical"]["cvar"],"#ff9f43"),
        ]:
            fig.add_vline(x=-val*100, line_dash="dash", line_color=col, line_width=2,
                          annotation_text=name, annotation_font_color=col, annotation_font_size=9)
        fig.update_layout(**PL, height=340, title="Portfolio Daily Return Distribution",
                          xaxis_title="Return (%)", yaxis_title="Frequency")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        corr = ret_df.corr()
        fig_c = px.imshow(corr,
                          color_continuous_scale=[[0,"#003366"],[0.5,"#1e3a5f"],[1,"#FFD700"]],
                          text_auto=".2f", aspect="auto", title="Correlation Matrix")
        fig_c.update_layout(**PL, height=340, coloraxis_showscale=False)
        fig_c.update_traces(textfont_size=9)
        st.plotly_chart(fig_c, use_container_width=True)

    # ── Multi-horizon ───────────────────────────────────────────────────────
    section_h(f"📅 Multi-Horizon Portfolio VaR — ₹{invest:,.0f}")
    hv1 = hist_r["Historical"]["var"]
    nv1 = hist_r["Normal"]["var"]
    rows = []
    for h in [1, 2, 5, 10, 21, 63, 252]:
        hv = scale_var(hv1, h)
        nv = scale_var(nv1, h)
        rows.append([f"{h}d", f"{hv*100:.3f}%", f"₹{hv*invest:,.0f}",
                     f"{nv*100:.3f}%", f"₹{nv*invest:,.0f}"])
    st.html(table_html(["Horizon","Hist VaR %","Hist VaR ₹","Normal VaR %","Normal VaR ₹"], rows))

    # ── Component VaR ───────────────────────────────────────────────────────
    section_h("🧩 Component VaR — Risk Attribution")
    col_a, col_b = st.columns([1, 1])
    with col_a:
        rows_c = [
            [row["Ticker"], f"{row['Weight (%)']:.1f}%",
             f"{row['Marginal VaR']:.5f}", f"{row['Component VaR']:.5f}",
             f"{row['% Contribution']:.1f}%"]
            for _, row in comp_df.iterrows()
        ]
        st.html(table_html(["Ticker","Weight","Marginal VaR","Component VaR","% Contrib"], rows_c))
    with col_b:
        fig_c = go.Figure(go.Bar(
            x=comp_df["Ticker"], y=comp_df["% Contribution"],
            marker_color=COLORS[:len(comp_df)],
            text=[f"{v:.1f}%" for v in comp_df["% Contribution"]],
            textposition="outside", textfont=dict(color="#e6f1ff", size=10)
        ))
        fig_c.update_layout(**PL, height=310, title="VaR Contribution by Stock",
                            yaxis_title="% Contribution to Portfolio VaR")
        st.plotly_chart(fig_c, use_container_width=True)

    # ── Incremental VaR ────────────────────────────────────────────────────
    section_h("➕ Incremental VaR")
    col_c, col_d = st.columns([1, 1])
    with col_c:
        rows_i = []
        for _, row in incr_df.iterrows():
            sign = "+" if row["Incremental VaR"] > 0 else ""
            c = "#dc3545" if row["Incremental VaR"] > 0 else "#28a745"
            rows_i.append([
                row["Ticker"],
                f'<span style="color:{c};-webkit-text-fill-color:{c}">{sign}{row["Incremental VaR"]:.5f}</span>',
                f'{sign}{row["% of Portfolio VaR"]:.2f}%'
            ])
        st.html(table_html(["Ticker","Incremental VaR","% Change in Port VaR"], rows_i))
    with col_d:
        inc_cols = ["#dc3545" if v > 0 else "#28a745" for v in incr_df["Incremental VaR"]]
        fig_i = go.Figure(go.Bar(
            x=incr_df["Ticker"], y=incr_df["Incremental VaR"]*100,
            marker_color=inc_cols,
            text=[f"{v*100:.4f}%" for v in incr_df["Incremental VaR"]],
            textposition="outside", textfont=dict(color="#e6f1ff", size=9)
        ))
        fig_i.update_layout(**PL, height=310, title="Incremental VaR (▲ = risk-increasing)",
                            yaxis_title="Incremental VaR (%)")
        st.plotly_chart(fig_i, use_container_width=True)

    # ── Diversification ────────────────────────────────────────────────────
    section_h("🌐 Diversification Benefit")
    d1 = hero_metric("Undiversified VaR", f"{div['undiversified_var']*100:.3f}%",
                     "Sum of individual VaRs", "down","#ff9f43")
    d2 = hero_metric("Portfolio VaR",     f"{div['portfolio_var']*100:.3f}%",
                     "After diversification",  "down","#28a745")
    d3 = hero_metric("Div. Benefit",      f"{div['diversification_benefit']*100:.3f}%",
                     "Risk reduction",         "up",  "#64ffda")
    d4 = hero_metric("Div. Ratio",        f"{div['diversification_ratio']:.3f}x",
                     ">1.0 = diversified",     "","#FFD700")
    st.html('<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:14px">'
            + "".join(f'<div>{m}</div>' for m in [d1,d2,d3,d4]) + '</div>')

    col_e, col_f = st.columns([2, 1])
    with col_e:
        fig_div = go.Figure()
        fig_div.add_trace(go.Bar(
            name="Individual VaRs", x=available,
            y=[(norm.ppf(conf_level) * ret_df[t].std()) * 100 for t in available],
            marker_color=COLORS[:len(available)]
        ))
        fig_div.add_trace(go.Bar(
            name="Portfolio VaR", x=["PORTFOLIO"],
            y=[div["portfolio_var"]*100], marker_color="#28a745"
        ))
        fig_div.add_hline(y=div["undiversified_var"]*100, line_dash="dash",
                          line_color="#FFD700", annotation_text="Undiversified Sum")
        fig_div.update_layout(**PL, height=320,
                               title="Individual VaRs vs Portfolio VaR",
                               yaxis_title="VaR (%)")
        st.plotly_chart(fig_div, use_container_width=True)
    with col_f:
        _undiv = f"{div['undiversified_var']*100:.3f}%"
        _port  = f"{div['portfolio_var']*100:.3f}%"
        _ben   = f"{div['diversification_benefit']*100:.3f}%"
        _ratio = div['diversification_ratio']
        _msg   = "diversification is reducing portfolio risk." if _ratio > 1 else "no diversification benefit."
        render_ib(
            f"{hl('Diversification Ratio')} = {_ratio:.3f}x<br><br>"
            f"Undiversified VaR = {hl(_undiv)}<br>"
            f"Portfolio VaR = {gt(_port)}<br>"
            f"Benefit = {acc(_ben)}<br><br>"
            f"A ratio {'> 1.0' if _ratio>1 else '= 1.0'} means {_msg}",
            "green" if _ratio > 1.02 else "amber"
        )

    # ── Extended shortfall ─────────────────────────────────────────────────
    section_h("🎯 Extended Shortfall — Portfolio")
    em = ext
    e1 = metric_card("Expected Shortfall",    f"{em['es']*100:.3f}%",           "≡ CVaR Historical",       "#ff9f43")
    e2 = metric_card("Stressed ES",           f"{em['stressed_es']*100:.3f}%",  "Worst 60-day window",     "#dc3545")
    e3 = metric_card("Spectral Risk Measure", f"{em['spectral_rm']*100:.3f}%",  "Exp-weighted tail",       "#a29bfe")
    e4 = metric_card("Entropic VaR",          f"{em['evar']*100:.3f}%",         "Upper bound to ES",       "#64ffda")
    e5 = metric_card("Range VaR (99−95%)",    f"{em['range_var']*100:.3f}%",    "VaR(99%) − VaR(95%)",     "#FFD700")
    st.html('<div style="display:grid;grid-template-columns:repeat(5,1fr);gap:10px;margin-bottom:14px">'
            + "".join(f'<div>{e}</div>' for e in [e1,e2,e3,e4,e5]) + '</div>')

    # ── Monte Carlo simulation fan ─────────────────────────────────────────
    section_h("🎲 Monte Carlo Portfolio Simulation")
    n_paths  = 200
    port_mu  = port_r.mean()
    port_sig = port_r.std()
    sim_paths = np.zeros((n_paths, horizon))
    for i in range(n_paths):
        sim_paths[i] = np.cumprod(1 + np.random.normal(port_mu, port_sig, horizon)) - 1
    fig_mc = go.Figure()
    for i in range(n_paths):
        clr = "#dc3545" if sim_paths[i, -1] < -mc_res["var"] else "#1e4a7a"
        fig_mc.add_trace(go.Scatter(
            x=list(range(1, horizon+1)), y=sim_paths[i]*100,
            mode="lines", line=dict(color=clr, width=0.6),
            showlegend=False, opacity=0.35
        ))
    p50 = np.percentile(sim_paths, 50, axis=0) * 100
    p5  = np.percentile(sim_paths, 5,  axis=0) * 100
    p1  = np.percentile(sim_paths, 1,  axis=0) * 100
    fig_mc.add_trace(go.Scatter(x=list(range(1,horizon+1)), y=p50, mode="lines",
                                name="Median", line=dict(color="#FFD700", width=2.5)))
    fig_mc.add_trace(go.Scatter(x=list(range(1,horizon+1)), y=p5, mode="lines",
                                name="5th Pct", line=dict(color="#ff9f43", width=2, dash="dash")))
    fig_mc.add_trace(go.Scatter(x=list(range(1,horizon+1)), y=p1, mode="lines",
                                name="1st Pct", line=dict(color="#dc3545", width=2, dash="dot")))
    fig_mc.update_layout(**PL, height=370,
                          title=f"Monte Carlo — {n_paths} Portfolio Paths over {horizon} Days",
                          xaxis_title="Trading Days", yaxis_title="Cumulative Return (%)")
    st.plotly_chart(fig_mc, use_container_width=True)

    # ── Efficient Frontier ─────────────────────────────────────────────────
    if len(available) >= 3:
        section_h("📈 Monte Carlo Efficient Frontier")
        n_port = 2000
        mus_v  = ret_df.mean().values
        cov_m  = ret_df.cov().values
        pvols, prets, psharpes = [], [], []
        for _ in range(n_port):
            rw = np.random.dirichlet(np.ones(len(available)))
            pv = np.sqrt(rw @ cov_m @ rw)
            pr = rw @ mus_v
            pvols.append(pv * np.sqrt(252) * 100)
            prets.append(pr * 252 * 100)
            psharpes.append(pr / pv if pv > 0 else 0)
        fig_ef = go.Figure()
        fig_ef.add_trace(go.Scatter(x=pvols, y=prets, mode="markers",
                                    marker=dict(color=psharpes, colorscale="Viridis",
                                                size=4, colorbar=dict(title="Sharpe"), opacity=0.7),
                                    name="Random Portfolios"))
        cur_vol = param["port_vol"] * np.sqrt(252) * 100
        cur_ret = port_r.mean() * 252 * 100
        fig_ef.add_trace(go.Scatter(x=[cur_vol], y=[cur_ret], mode="markers",
                                    marker=dict(color="#FFD700", size=16, symbol="star"),
                                    name="Current Portfolio"))
        fig_ef.update_layout(**PL, height=370, title="Monte Carlo Efficient Frontier",
                              xaxis_title="Annual Volatility (%)", yaxis_title="Annual Return (%)")
        st.plotly_chart(fig_ef, use_container_width=True)

    # ── Portfolio statistics table ─────────────────────────────────────────
    section_h("📋 Portfolio Statistics")
    st.html(table_html(
        ["Statistic", "Value"],
        [
            ["Mean Daily Return",         f"{port_stats['mean_daily']*100:.4f}%"],
            ["Mean Annual Return",        f"{port_stats['mean_annual']*100:.2f}%"],
            ["Daily Volatility",          f"{port_stats['vol_daily']*100:.4f}%"],
            ["Annual Volatility",         f"{port_stats['vol_annual']*100:.2f}%"],
            ["Portfolio Skewness",        f"{port_stats['skewness']:.4f}"],
            ["Portfolio Excess Kurtosis", f"{port_stats['excess_kurt']:.4f}"],
            ["Sharpe Ratio",              f"{port_stats['sharpe']:.4f}"],
            ["Maximum Drawdown",          f"{port_stats['max_drawdown']*100:.2f}%"],
            ["Observations",              str(port_stats["n_obs"])],
        ]
    ))

    # ── Formula block ──────────────────────────────────────────────────────
    section_h("📚 Portfolio VaR Formulae")
    st.html(fml(
        "Portfolio Return:     r_p = Σ w_i · r_i\n"
        "Portfolio Variance:   σ²_p = w' Σ w    (Σ = covariance matrix)\n"
        "Parametric VaR:       VaR_p = −(μ_p + z_α · σ_p)\n"
        "Parametric CVaR:      CVaR_p = −(μ_p − σ_p · φ(z_α) / α)\n\n"
        "Marginal VaR_i:       = (Σ w)_i / σ_p · z_α\n"
        "Component VaR_i:      = w_i · Marginal VaR_i\n"
        "Σ Component VaR_i     = Portfolio VaR   (Euler homogeneity theorem)\n\n"
        "Diversification Ratio = Σ(w_i · Indiv VaR_i) / Portfolio VaR ≥ 1\n"
        "MC VaR (Cholesky):    Σ = L·L'  →  sim = z·L' + μ,   z ~ N(0,I)"
    ))
