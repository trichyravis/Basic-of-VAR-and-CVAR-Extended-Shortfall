"""tab_single.py — Single Stock VaR / CVaR / ES  (v2 redesign)"""
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.stats import norm

from components import (
    section_h, render_card, ib, render_ib, fml, bdg,
    metric_card, hero_metric, table_html,
    four_col, three_col, two_col, five_col, six_col,
    tab_banner, var_result_card, stat_box,
    NO_SEL, FH, FB, FM, TXT, hl, gt, rt, lb, org, pur, acc, p
)
from var_engine import (
    all_var_methods, extended_shortfall_metrics,
    rolling_var, backtesting_kupiec, descriptive_stats, scale_var
)

PL = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(13,31,58,0.55)",
    font=dict(family="Source Sans Pro", color="#e6f1ff"),
    xaxis=dict(gridcolor="#1e3a5f", showgrid=True, zeroline=False),
    yaxis=dict(gridcolor="#1e3a5f", showgrid=True, zeroline=False),
    legend=dict(bgcolor="rgba(17,34,64,0.9)", bordercolor="#1e3a5f", borderwidth=1),
    margin=dict(l=20, r=20, t=50, b=20),
)
COLORS = ["#FFD700","#ADD8E6","#64ffda","#ff9f43","#a29bfe","#28a745","#dc3545","#00cec9"]


def tab_single(prices_df, ticker, conf_level, horizon, n_sims, invest, ret_method):

    if prices_df is None or ticker not in prices_df.columns:
        st.warning("⚠️ Please fetch stock data from the sidebar first.")
        return

    px_s = prices_df[ticker].dropna()
    if len(px_s) < 30:
        st.error("Need at least 30 trading days of data.")
        return

    rets = (np.log(px_s / px_s.shift(1)) if ret_method == "Log Returns"
            else px_s.pct_change()).dropna().values

    stats_d = descriptive_stats(rets, ticker)
    results = all_var_methods(rets, conf_level, n_sims)
    ext     = extended_shortfall_metrics(rets, conf_level)

    # ── Tab banner ─────────────────────────────────────────────────────────
    tab_banner(
        f"📈 {ticker} — Single Stock VaR / CVaR / ES",
        f"Confidence: {conf_level*100:.0f}%  |  Horizon: {horizon}d  |  "
        f"Investment: ₹{invest:,.0f}  |  Method: {ret_method}  |  Obs: {len(rets)}"
    )

    # ── Hero metric row ─────────────────────────────────────────────────────
    ref_v  = results["Historical"]["var"]
    ref_cv = results["Historical"]["cvar"]
    h1 = hero_metric("Hist VaR 1-Day",   f"{ref_v*100:.2f}%",  f"₹{ref_v*invest:,.0f} loss",  "down","#dc3545")
    h2 = hero_metric("Hist CVaR 1-Day",  f"{ref_cv*100:.2f}%", f"₹{ref_cv*invest:,.0f} loss", "down","#ff9f43")
    h3 = hero_metric(f"VaR {horizon}d",  f"{scale_var(ref_v,horizon)*100:.2f}%",
                     f"₹{scale_var(ref_v,horizon)*invest:,.0f}","down","#FFD700")
    h4 = hero_metric("Ann. Volatility",   f"{stats_d['vol_annual']*100:.2f}%",
                     f"Daily σ {stats_d['vol_daily']*100:.2f}%","","#ADD8E6")
    h5 = hero_metric("Sharpe Ratio",      f"{stats_d['sharpe']:.3f}",
                     f"Max DD {stats_d['max_drawdown']*100:.2f}%","","#64ffda")
    st.html(f'<div style="display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin-bottom:18px">'
            f'<div>{h1}</div><div>{h2}</div><div>{h3}</div><div>{h4}</div><div>{h5}</div></div>')

    # ── All 7 VaR method cards ──────────────────────────────────────────────
    section_h("📐 All 7 VaR / CVaR Methods Compared")
    icons_map = {"Historical":"📊","Normal":"📈","Student-t":"📉",
                 "Cornish-Fisher":"🌀","Monte Carlo":"🎲","EWMA":"⚡","GARCH(1,1)":"🔥"}
    col_map   = {"Historical":"#ADD8E6","Normal":"#FFD700","Student-t":"#64ffda",
                 "Cornish-Fisher":"#ff9f43","Monte Carlo":"#a29bfe","EWMA":"#28a745","GARCH(1,1)":"#dc3545"}
    cards = [var_result_card(f"{icons_map.get(k,'📐')} {k}",
                             f"{r['var']*100:.3f}%",
                             f"{r['cvar']*100:.3f}%",
                             col_map.get(k,"#FFD700"))
             for k, r in results.items()]
    st.html('<div style="display:grid;grid-template-columns:repeat(7,1fr);gap:9px;margin-bottom:14px">'
            + "".join(f'<div>{c}</div>' for c in cards) + '</div>')

    # ── Charts — VaR comparison + distribution ──────────────────────────────
    section_h("📊 VaR & CVaR Comparison + Return Distribution")
    col1, col2 = st.columns([1, 1])

    methods   = list(results.keys())
    var_vals  = [results[m]["var"]  * 100 for m in methods]
    cvar_vals = [results[m]["cvar"] * 100 for m in methods]

    with col1:
        fig = go.Figure()
        fig.add_trace(go.Bar(name="VaR", x=methods, y=var_vals,
                             marker_color="#ADD8E6",
                             text=[f"{v:.3f}%" for v in var_vals], textposition="outside",
                             textfont=dict(size=9)))
        fig.add_trace(go.Bar(name="CVaR / ES", x=methods, y=cvar_vals,
                             marker_color="#FFD700",
                             text=[f"{v:.3f}%" for v in cvar_vals], textposition="outside",
                             textfont=dict(size=9)))
        fig.update_layout(**PL, title=f"{ticker} — VaR vs CVaR by Method ({conf_level*100:.0f}% CL)",
                          barmode="group", height=360, yaxis_title="Loss (%)")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = go.Figure()
        fig2.add_trace(go.Histogram(x=rets*100, nbinsx=80, marker_color="#004d80",
                                    opacity=0.75, name="Returns"))
        x_r = np.linspace(rets.min(), rets.max(), 300)
        y_n = norm.pdf(x_r, np.mean(rets), np.std(rets))
        y_n = y_n / y_n.max() * (len(rets) / 20)
        fig2.add_trace(go.Scatter(x=x_r*100, y=y_n, mode="lines",
                                  line=dict(color="#64ffda", width=2), name="Normal Fit"))
        for i, (method, res) in enumerate(results.items()):
            fig2.add_vline(x=-res["var"]*100, line_dash="dash",
                           line_color=COLORS[i], line_width=1.5,
                           annotation_text=f"{method[:4]}",
                           annotation_font_color=COLORS[i], annotation_font_size=8)
        fig2.update_layout(**PL, title=f"{ticker} — Return Distribution + VaR Lines",
                           height=360, xaxis_title="Return (%)", yaxis_title="Frequency")
        st.plotly_chart(fig2, use_container_width=True)

    # ── Price & returns history ─────────────────────────────────────────────
    section_h("💹 Price & Returns History")
    fig3 = make_subplots(rows=2, cols=1, shared_xaxes=True,
                          row_heights=[0.65, 0.35], vertical_spacing=0.05)
    fig3.add_trace(go.Scatter(x=px_s.index, y=px_s.values, mode="lines", name="Price",
                              line=dict(color="#FFD700", width=2)), row=1, col=1)
    ret_colors = ["#dc3545" if r < 0 else "#28a745" for r in rets]
    fig3.add_trace(go.Bar(x=px_s.index[1:], y=rets*100, name="Daily Return",
                          marker_color=ret_colors), row=2, col=1)
    fig3.update_layout(**PL, height=460, title=f"{ticker} — Price & Daily Returns", showlegend=False)
    fig3.update_yaxes(title_text="Price (₹)", row=1, col=1, gridcolor="#1e3a5f")
    fig3.update_yaxes(title_text="Return (%)", row=2, col=1, gridcolor="#1e3a5f")
    st.plotly_chart(fig3, use_container_width=True)

    # ── Multi-horizon scaling ───────────────────────────────────────────────
    section_h("📅 Multi-Horizon VaR Scaling (√T Rule)")
    hv1 = results["Historical"]["var"]
    nv1 = results["Normal"]["var"]
    hrows = []
    for h in [1, 2, 5, 10, 21, 63, 252]:
        hv = scale_var(hv1, h)
        nv = scale_var(nv1, h)
        hrows.append([f"{h}d", f"{hv*100:.3f}%", f"₹{hv*invest:,.0f}",
                      f"{nv*100:.3f}%", f"₹{nv*invest:,.0f}"])
    st.html(table_html(["Horizon","Hist VaR %","Hist VaR ₹","Normal VaR %","Normal VaR ₹"], hrows))
    render_ib(
        f"VaR scaling uses the {hl('√T rule')} — T-day VaR = 1-day VaR × √T. "
        f"Basel 10-day VaR = 1-day VaR × √10 = {np.sqrt(10):.3f}×. "
        f"Valid only under the {hl('i.i.d. returns assumption')} (GARCH scaling differs).", "blue"
    )

    # ── Extended shortfall metrics ──────────────────────────────────────────
    section_h("🎯 Extended Shortfall & Tail Risk Metrics")
    em = ext
    e1 = metric_card("Expected Shortfall",   f"{em['es']*100:.3f}%",     "≡ CVaR (Historical)", "#ff9f43")
    e2 = metric_card("Stressed ES",          f"{em['stressed_es']*100:.3f}%", "Worst 60-day period",  "#dc3545")
    e3 = metric_card("Spectral Risk Measure",f"{em['spectral_rm']*100:.3f}%", "Exp-weighted tail",   "#a29bfe")
    e4 = metric_card("Entropic VaR",         f"{em['evar']*100:.3f}%",   "Upper bound to ES",   "#64ffda")
    e5 = metric_card("Range VaR (99−95%)",   f"{em['range_var']*100:.3f}%","Tail risk spread",   "#FFD700")
    st.html('<div style="display:grid;grid-template-columns:repeat(5,1fr);gap:10px;margin-bottom:14px">'
            f'<div>{e1}</div><div>{e2}</div><div>{e3}</div><div>{e4}</div><div>{e5}</div></div>')

    es_methods = ["ES (Hist)","Stressed ES","Spectral RM","Entropic VaR","Range VaR","VaR@99%","VaR@95%"]
    es_values  = [em["es"], em["stressed_es"], em["spectral_rm"], em["evar"],
                  em["range_var"], em["var_99"], em["var_95"]]
    fig4 = go.Figure(go.Bar(x=es_methods, y=[v*100 for v in es_values],
                             marker_color=COLORS,
                             text=[f"{v*100:.3f}%" for v in es_values],
                             textposition="outside", textfont=dict(color="#e6f1ff", size=10)))
    fig4.update_layout(**PL, height=330, title="Extended Shortfall & Tail Risk Measures",
                       yaxis_title="Risk Measure (%)")
    st.plotly_chart(fig4, use_container_width=True)

    # ── Rolling VaR ────────────────────────────────────────────────────────
    section_h("📈 Rolling VaR — 63-Day Window")
    rh = rolling_var(rets, window=63, cl=conf_level, method="hist")
    rn = rolling_var(rets, window=63, cl=conf_level, method="norm")
    idx = px_s.index[-len(rh):]
    fig5 = go.Figure()
    fig5.add_trace(go.Scatter(x=idx, y=rh.values*100, mode="lines",
                              name="Rolling Hist VaR", line=dict(color="#FFD700", width=2)))
    fig5.add_trace(go.Scatter(x=idx, y=rn.values*100, mode="lines",
                              name="Rolling Normal VaR", line=dict(color="#ADD8E6", width=2)))
    fig5.update_layout(**PL, height=330,
                       title=f"Rolling 63-Day VaR ({conf_level*100:.0f}% CL)", yaxis_title="VaR (%)")
    st.plotly_chart(fig5, use_container_width=True)

    # ── Kupiec POF Backtest ─────────────────────────────────────────────────
    section_h("🔬 Kupiec POF Backtest")
    var_s     = rolling_var(rets, window=63, cl=conf_level, method="hist").values
    align_r   = rets[-len(var_s):]
    bt        = backtesting_kupiec(align_r, var_s, conf_level)
    pass_col  = "#28a745" if bt["pass"] else "#dc3545"
    b1 = metric_card("Exceptions",     str(bt["exceptions"]),       f"Expected: {bt['expected']}", "#FFD700")
    b2 = metric_card("Exception Rate", f"{bt['exception_rate']}%",  f"Expected: {bt['expected_rate']}%", "#ADD8E6")
    b3 = metric_card("LR Statistic",   f"{bt['lr_statistic']:.4f}", "χ²(1) test", "#ff9f43")
    b4 = metric_card("p-value",        f"{bt['p_value']:.4f}",      "H₀: correct VaR", "#a29bfe")
    b5 = metric_card("Backtest Result","PASS ✅" if bt["pass"] else "FAIL ❌", "p > 0.05 = pass", pass_col)
    st.html('<div style="display:grid;grid-template-columns:repeat(5,1fr);gap:10px;margin-bottom:14px">'
            + "".join(f'<div>{m}</div>' for m in [b1,b2,b3,b4,b5]) + '</div>')
    render_ib(
        f"{hl('Kupiec POF Test')} — H₀: exception rate = (1−CL). LR stat ~ χ²(1). "
        f"Reject H₀ if p < 0.05. "
        f"{'✅ VaR model accepted at 5% significance.' if bt['pass'] else '❌ VaR model rejected — recalibrate.'}",
        "green" if bt["pass"] else "red"
    )

    # ── Descriptive statistics ──────────────────────────────────────────────
    section_h("📋 Descriptive Statistics")
    col_a, col_b = st.columns([1, 1])
    with col_a:
        st.html(table_html(
            ["Statistic", "Daily", "Annual"],
            [
                ["Mean Return",     f"{stats_d['mean_daily']*100:.4f}%",   f"{stats_d['mean_annual']*100:.2f}%"],
                ["Volatility",      f"{stats_d['vol_daily']*100:.4f}%",    f"{stats_d['vol_annual']*100:.2f}%"],
                ["Skewness",        f"{stats_d['skewness']:.4f}",           "—"],
                ["Excess Kurtosis", f"{stats_d['excess_kurt']:.4f}",        "—"],
                ["Min (Worst Day)", f"{stats_d['min']*100:.3f}%",           "—"],
                ["Max (Best Day)",  f"{stats_d['max']*100:.3f}%",           "—"],
                ["Sharpe Ratio",    "—",                                     f"{stats_d['sharpe']:.4f}"],
                ["Max Drawdown",    "—",                                     f"{stats_d['max_drawdown']*100:.2f}%"],
                ["Observations",    str(stats_d["n_obs"]),                  "—"],
                ["Jarque-Bera p",   f"{stats_d['jb_pvalue']:.4f}",
                 "✅ Normal" if stats_d["is_normal"] else "❌ Non-Normal"],
            ]
        ))
    with col_b:
        # Q-Q style distribution stats radar via bar
        labels = ["Skewness\n(abs)", "Exc. Kurt\n(norm)", "Jarque-Bera\n(norm)", "Tail Risk\n(norm)"]
        skew_n = min(abs(stats_d["skewness"]) / 2, 1)
        kurt_n = min(abs(stats_d["excess_kurt"]) / 6, 1)
        jb_n   = 1 - min(stats_d["jb_pvalue"], 1)
        tail_n = min(ext["es"] / 0.05, 1)
        vals   = [skew_n, kurt_n, jb_n, tail_n]
        bar_colors = ["#ff9f43" if v > 0.5 else "#28a745" for v in vals]
        fig_s = go.Figure(go.Bar(x=labels, y=[v*100 for v in vals],
                                  marker_color=bar_colors,
                                  text=[f"{v*100:.0f}" for v in vals], textposition="outside",
                                  textfont=dict(color="#e6f1ff")))
        fig_s.update_layout(**PL, height=300, title="Distribution Risk Indicators (0=low, 100=high)",
                            yaxis_title="Risk Score", yaxis_range=[0, 115])
        st.plotly_chart(fig_s, use_container_width=True)

    # ── Formula reference ───────────────────────────────────────────────────
    section_h("📚 VaR Formula Reference")
    render_card("Key Formulae", fml(
        "Historical VaR(α)   = −Quantile(Returns, α)\n"
        "Normal VaR(α)       = −(μ + z_α × σ)          z_α = Φ⁻¹(α)\n"
        "Student-t VaR(α)    = −(μ + t⁻¹(α,ν) × σ)    ν = fitted dof\n"
        "Cornish-Fisher VaR  = −(μ + z_CF × σ)         z_CF = z + (z²-1)S/6 + (z³-3z)K/24\n"
        "Monte Carlo VaR     = −Quantile(Simulated, α)\n"
        "EWMA σ²(t)          = λ·σ²(t-1) + (1-λ)·r²(t-1)    λ=0.94\n"
        "GARCH(1,1) σ²(t)    = ω + α·ε²(t-1) + β·h(t-1)\n\n"
        "CVaR / ES           = E[Loss | Loss > VaR]   (average tail loss beyond VaR)\n"
        f"T-day VaR           = VaR(1d) × √T            (Basel √T rule)"
    ), "#FFD700")
