"""tab_single.py — Single Stock VaR / CVaR / ES analysis"""
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
from var_engine import (all_var_methods, extended_shortfall_metrics,
                        rolling_var, backtesting_kupiec, descriptive_stats,
                        scale_var)

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(13,31,58,0.6)",
    font=dict(family="Source Sans Pro", color="#e6f1ff"),
    xaxis=dict(gridcolor="#1e3a5f", showgrid=True, zeroline=False),
    yaxis=dict(gridcolor="#1e3a5f", showgrid=True, zeroline=False),
    legend=dict(bgcolor="rgba(17,34,64,0.9)", bordercolor="#1e3a5f", borderwidth=1),
    margin=dict(l=20, r=20, t=50, b=20),
)


def tab_single(prices_df: pd.DataFrame, ticker: str, conf_level: float,
               horizon: int, n_sims: int, invest: float, ret_method: str):
    """Full single-stock VaR analysis tab."""

    if prices_df is None or ticker not in prices_df.columns:
        st.warning("⚠️ Please load stock data from the sidebar first.")
        return

    px_series = prices_df[ticker].dropna()
    if len(px_series) < 30:
        st.error("Need at least 30 trading days of data.")
        return

    if ret_method == "Log Returns":
        rets = np.log(px_series / px_series.shift(1)).dropna().values
    else:
        rets = px_series.pct_change().dropna().values

    stats_d = descriptive_stats(rets, ticker)
    results = all_var_methods(rets, conf_level, n_sims)
    ext     = extended_shortfall_metrics(rets, conf_level)

    # ── Hero metrics ─────────────────────────────────────────────
    st.html(
        f'<div style="background:linear-gradient(135deg,#003366,#004d80);'
        f'border-radius:12px;padding:20px 24px;margin-bottom:16px;{NO_SEL}">'
        f'<span style="font-family:{FH};color:#FFD700;-webkit-text-fill-color:#FFD700;'
        f'font-size:1.6rem;font-weight:700">{ticker}</span>'
        f'<span style="color:#8892b0;-webkit-text-fill-color:#8892b0;'
        f'font-family:{FB};font-size:.9rem;margin-left:16px">'
        f'Confidence: {conf_level*100:.0f}% | Horizon: {horizon}d | '
        f'Investment: ₹{invest:,.0f}</span></div>'
    )

    ref_var = results["Historical"]["var"]
    ref_cvar = results["Historical"]["cvar"]
    m1 = metric_card("Hist VaR (1-Day)", f"{ref_var*100:.2f}%",
                     f"₹{ref_var*invest:,.0f} loss", "#dc3545")
    m2 = metric_card("Hist CVaR (1-Day)", f"{ref_cvar*100:.2f}%",
                     f"₹{ref_cvar*invest:,.0f} loss", "#ff9f43")
    m3 = metric_card(f"Hist VaR ({horizon}d)", f"{scale_var(ref_var, horizon)*100:.2f}%",
                     f"₹{scale_var(ref_var, horizon)*invest:,.0f}", "#FFD700")
    m4 = metric_card("Annual Volatility", f"{stats_d['vol_annual']*100:.2f}%",
                     f"Daily σ: {stats_d['vol_daily']*100:.2f}%", "#ADD8E6")
    m5 = metric_card("Sharpe Ratio", f"{stats_d['sharpe']:.3f}",
                     f"Max DD: {stats_d['max_drawdown']*100:.2f}%", "#64ffda")
    st.html(f'<div style="display:grid;grid-template-columns:repeat(5,1fr);gap:10px;margin-bottom:14px">'
            f'<div>{m1}</div><div>{m2}</div><div>{m3}</div><div>{m4}</div><div>{m5}</div></div>')

    # ── All VaR Methods Comparison ────────────────────────────────
    section_h("📐 All VaR Methods Comparison")
    icons = {"Historical":"📊","Normal":"📈","Student-t":"📉",
             "Cornish-Fisher":"🌀","Monte Carlo":"🎲","EWMA":"⚡","GARCH(1,1)":"🔥"}
    colors_map = {
        "Historical":"#ADD8E6","Normal":"#FFD700","Student-t":"#64ffda",
        "Cornish-Fisher":"#ff9f43","Monte Carlo":"#a29bfe","EWMA":"#28a745","GARCH(1,1)":"#dc3545"
    }
    cols_var = st.columns(7)
    for i, (k, res) in enumerate(results.items()):
        v_pct = f"{res['var']*100:.2f}%"
        c_pct = f"{res['cvar']*100:.2f}%"
        with cols_var[i]:
            st.html(var_result_card(icons.get(k,"📐")+" "+k, v_pct, c_pct, colors_map.get(k,"#FFD700")))

    # ── VaR Comparison bar chart ──────────────────────────────────
    section_h("📊 VaR & CVaR Comparison Chart")
    methods = list(results.keys())
    var_vals  = [results[m]["var"]  * 100 for m in methods]
    cvar_vals = [results[m]["cvar"] * 100 for m in methods]
    es_vals   = [results[m]["es"]   * 100 for m in methods]

    fig = go.Figure()
    fig.add_trace(go.Bar(name="VaR", x=methods, y=var_vals,
                         marker_color="#ADD8E6", text=[f"{v:.3f}%" for v in var_vals],
                         textposition="outside", textfont=dict(size=10)))
    fig.add_trace(go.Bar(name="CVaR / ES", x=methods, y=cvar_vals,
                         marker_color="#FFD700", text=[f"{v:.3f}%" for v in cvar_vals],
                         textposition="outside", textfont=dict(size=10)))
    fig.update_layout(**PLOTLY_LAYOUT, title=f"{ticker} — VaR vs CVaR by Method ({conf_level*100:.0f}% CL)",
                      barmode="group", height=380,
                      yaxis_title="Loss (%)")
    st.plotly_chart(fig, use_container_width=True)

    # ── Return distribution + VaR lines ──────────────────────────
    section_h("📉 Return Distribution with VaR / CVaR Overlays")
    fig2 = go.Figure()
    # Histogram of returns
    fig2.add_trace(go.Histogram(x=rets * 100, nbinsx=80,
                                marker_color="#004d80", marker_line_color="#1e3a5f",
                                opacity=0.7, name="Returns"))
    # Normal distribution overlay
    x_range = np.linspace(rets.min(), rets.max(), 300)
    y_norm   = norm.pdf(x_range, np.mean(rets), np.std(rets))
    y_norm   = y_norm / y_norm.max() * (len(rets) / 20)
    fig2.add_trace(go.Scatter(x=x_range * 100, y=y_norm, mode="lines",
                              line=dict(color="#64ffda", width=2), name="Normal Fit"))

    # VaR lines
    line_colors = ["#FFD700","#ADD8E6","#ff9f43","#a29bfe","#28a745","#dc3545","#00cec9"]
    for i, (method, res) in enumerate(results.items()):
        fig2.add_vline(x=-res["var"]*100, line_dash="dash",
                       line_color=line_colors[i], line_width=1.5,
                       annotation_text=f"{method[:4]} VaR",
                       annotation_font_color=line_colors[i],
                       annotation_font_size=9)
    fig2.update_layout(**PLOTLY_LAYOUT, height=360,
                       title=f"{ticker} — Daily Return Distribution + VaR Lines",
                       xaxis_title="Return (%)", yaxis_title="Frequency")
    st.plotly_chart(fig2, use_container_width=True)

    # ── Multi-horizon VaR table ───────────────────────────────────
    section_h("📅 Multi-Horizon VaR Scaling (√T Rule)")
    hist_var_1d = results["Historical"]["var"]
    norm_var_1d = results["Normal"]["var"]
    horizons = [1, 2, 5, 10, 21, 63, 252]
    rows = []
    for h in horizons:
        hv = scale_var(hist_var_1d, h)
        nv = scale_var(norm_var_1d, h)
        rows.append([
            f"{h}d",
            f"{hv*100:.3f}%", f"₹{hv*invest:,.0f}",
            f"{nv*100:.3f}%", f"₹{nv*invest:,.0f}",
        ])
    st.html(table_html(
        ["Horizon", "Hist VaR %", "Hist VaR ₹", "Normal VaR %", "Normal VaR ₹"],
        rows
    ))
    render_ib(f"VaR scaling uses the {hl('√T rule')} — 10-day Basel VaR = 1-day VaR × √10 = "
              f"1-day VaR × {np.sqrt(10):.3f}. Valid only under i.i.d. returns assumption.", "blue")

    # ── Extended Shortfall metrics ────────────────────────────────
    section_h("🎯 Extended Shortfall Metrics")
    em = ext
    e1 = metric_card("Expected Shortfall",   f"{em['es']*100:.3f}%",     "≡ CVaR (Historical)", "#ff9f43")
    e2 = metric_card("Stressed ES",          f"{em['stressed_es']*100:.3f}%", "Worst 60-day period",  "#dc3545")
    e3 = metric_card("Spectral Risk Measure",f"{em['spectral_rm']*100:.3f}%", "Exp-weighted tail",   "#a29bfe")
    e4 = metric_card("Entropic VaR",         f"{em['evar']*100:.3f}%",   "Upper bound to ES",   "#64ffda")
    e5 = metric_card("Range VaR (99-95%)",   f"{em['range_var']*100:.3f}%", "Tail risk spread",    "#FFD700")
    st.html(f'<div style="display:grid;grid-template-columns:repeat(5,1fr);gap:10px;margin-bottom:14px">'
            f'<div>{e1}</div><div>{e2}</div><div>{e3}</div><div>{e4}</div><div>{e5}</div></div>')

    # Extended shortfall comparison chart
    es_methods = ["ES (Hist)","Stressed ES","Spectral RM","Entropic VaR","Range VaR",
                  "VaR@99%","VaR@95%"]
    es_values  = [em["es"], em["stressed_es"], em["spectral_rm"], em["evar"],
                  em["range_var"], em["var_99"], em["var_95"]]
    es_colors  = ["#ff9f43","#dc3545","#a29bfe","#64ffda","#FFD700","#ADD8E6","#28a745"]

    fig3 = go.Figure(go.Bar(
        x=es_methods, y=[v*100 for v in es_values],
        marker_color=es_colors,
        text=[f"{v*100:.3f}%" for v in es_values],
        textposition="outside", textfont=dict(color="#e6f1ff", size=10)
    ))
    fig3.update_layout(**PLOTLY_LAYOUT, height=340,
                       title="Extended Shortfall & Tail Risk Measures",
                       yaxis_title="Risk Measure (%)")
    st.plotly_chart(fig3, use_container_width=True)

    # ── Rolling VaR ──────────────────────────────────────────────
    section_h("📈 Rolling VaR (63-day window)")
    roll_hist = rolling_var(rets, window=63, cl=conf_level, method="hist")
    roll_norm = rolling_var(rets, window=63, cl=conf_level, method="norm")
    idx       = px_series.index[-(len(roll_hist)):]

    fig4 = go.Figure()
    fig4.add_trace(go.Scatter(x=idx, y=roll_hist.values * 100, mode="lines",
                              name="Rolling Hist VaR", line=dict(color="#FFD700", width=2)))
    fig4.add_trace(go.Scatter(x=idx, y=roll_norm.values * 100, mode="lines",
                              name="Rolling Normal VaR", line=dict(color="#ADD8E6", width=2)))
    fig4.update_layout(**PLOTLY_LAYOUT, height=340,
                       title=f"Rolling 63-Day VaR ({conf_level*100:.0f}% CL)",
                       yaxis_title="VaR (%)")
    st.plotly_chart(fig4, use_container_width=True)

    # ── Backtest ─────────────────────────────────────────────────
    section_h("🔬 Kupiec POF Backtest")
    var_series_hist = rolling_var(rets, window=63, cl=conf_level, method="hist").values
    aligned_rets    = rets[-(len(var_series_hist)):]
    bt = backtesting_kupiec(aligned_rets, var_series_hist, conf_level)

    b1 = metric_card("Exceptions",     str(bt["exceptions"]),       f"Expected: {bt['expected']}", "#FFD700")
    b2 = metric_card("Exception Rate", f"{bt['exception_rate']}%",  f"Expected: {bt['expected_rate']}%", "#ADD8E6")
    b3 = metric_card("LR Statistic",   f"{bt['lr_statistic']:.4f}", "χ²(1) test",     "#ff9f43")
    b4 = metric_card("p-value",        f"{bt['p_value']:.4f}",      "H₀: correct VaR", "#a29bfe")
    pass_color = "#28a745" if bt["pass"] else "#dc3545"
    b5 = metric_card("Backtest Result", "PASS ✅" if bt["pass"] else "FAIL ❌",
                     "p > 0.05 = pass", pass_color)
    st.html(f'<div style="display:grid;grid-template-columns:repeat(5,1fr);gap:10px;margin-bottom:14px">'
            f'<div>{b1}</div><div>{b2}</div><div>{b3}</div><div>{b4}</div><div>{b5}</div></div>')

    render_ib(
        f"{hl('Kupiec POF Test')} — H₀: exception rate = (1−CL). "
        f"LR stat ~ χ²(1). Reject H₀ if p < 0.05 (model mispecified). "
        f"{'✅ VaR model accepted at 5% significance.' if bt['pass'] else '❌ VaR model rejected — recalibrate.'}",
        "green" if bt["pass"] else "red"
    )

    # ── Descriptive Statistics ────────────────────────────────────
    section_h("📋 Descriptive Statistics")
    st.html(table_html(
        ["Statistic", "Daily", "Annual"],
        [
            ["Mean Return",   f"{stats_d['mean_daily']*100:.4f}%",  f"{stats_d['mean_annual']*100:.2f}%"],
            ["Volatility",    f"{stats_d['vol_daily']*100:.4f}%",   f"{stats_d['vol_annual']*100:.2f}%"],
            ["Skewness",      f"{stats_d['skewness']:.4f}",          "—"],
            ["Excess Kurtosis",f"{stats_d['excess_kurt']:.4f}",      "—"],
            ["Min (Worst)",   f"{stats_d['min']*100:.3f}%",          "—"],
            ["Max (Best)",    f"{stats_d['max']*100:.3f}%",          "—"],
            ["Sharpe Ratio",  "—",                                    f"{stats_d['sharpe']:.4f}"],
            ["Max Drawdown",  "—",                                    f"{stats_d['max_drawdown']*100:.2f}%"],
            ["Observations",  str(stats_d["n_obs"]),                  "—"],
            ["Jarque-Bera p", f"{stats_d['jb_pvalue']:.4f}",
             "✅ Normal" if stats_d["is_normal"] else "❌ Non-Normal"],
        ]
    ))

    # ── Price chart ───────────────────────────────────────────────
    section_h("💹 Price & Returns History")
    fig5 = make_subplots(rows=2, cols=1, shared_xaxes=True,
                          row_heights=[0.65, 0.35], vertical_spacing=0.05)
    fig5.add_trace(go.Scatter(x=px_series.index, y=px_series.values, mode="lines",
                              name="Price", line=dict(color="#FFD700", width=2)), row=1, col=1)
    ret_colors = ["#dc3545" if r < 0 else "#28a745" for r in rets]
    fig5.add_trace(go.Bar(x=px_series.index[1:], y=rets * 100, name="Daily Return",
                          marker_color=ret_colors), row=2, col=1)
    fig5.update_layout(**PLOTLY_LAYOUT, height=480,
                       title=f"{ticker} — Price & Daily Returns",
                       showlegend=False)
    fig5.update_yaxes(title_text="Price (₹)", row=1, col=1, gridcolor="#1e3a5f")
    fig5.update_yaxes(title_text="Return (%)", row=2, col=1, gridcolor="#1e3a5f")
    st.plotly_chart(fig5, use_container_width=True)

    # ── Formula Box ───────────────────────────────────────────────
    section_h("📚 VaR Method Formulae")
    st.html(fml(
        "Historical VaR(α)  = -Quantile(Returns, α)\n"
        "Normal VaR(α)      = -(μ + z_α × σ)    where z_α = Φ⁻¹(α)\n"
        "Student-t VaR(α)   = -(μ + t⁻¹(α,ν) × σ)    ν = fitted degrees of freedom\n"
        "Cornish-Fisher VaR = -(μ + z_CF × σ)   z_CF = z + (z²-1)S/6 + (z³-3z)K/24 - (2z³-5z)S²/36\n"
        "Monte Carlo VaR    = -Quantile(Simulated Returns, α)\n"
        "EWMA Var(t)        = λ·σ²(t-1) + (1-λ)·r²(t-1)   λ=0.94\n"
        "GARCH(1,1)         = ω + α·ε²(t-1) + β·h(t-1)\n\n"
        f"CVaR / ES          = E[Loss | Loss > VaR]   (tail average beyond VaR)\n"
        f"Scaling:           = VaR(1d) × √T   (Basel √T rule for T-day horizon)"
    ))
