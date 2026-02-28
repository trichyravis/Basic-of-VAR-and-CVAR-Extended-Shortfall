"""tab_stress.py — Stress Testing & Scenario Analysis"""
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from components import (section_h, render_card, ib, render_ib, fml, bdg,
                        metric_card, table_html, NO_SEL, FH, FB, FM, TXT,
                        hl, gt, rt, lb, mut, p)
from var_engine import portfolio_returns, descriptive_stats

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(13,31,58,0.6)",
    font=dict(family="Source Sans Pro", color="#e6f1ff"),
    xaxis=dict(gridcolor="#1e3a5f", showgrid=True, zeroline=False),
    yaxis=dict(gridcolor="#1e3a5f", showgrid=True, zeroline=False),
    legend=dict(bgcolor="rgba(17,34,64,0.9)", bordercolor="#1e3a5f", borderwidth=1),
    margin=dict(l=20, r=20, t=50, b=20),
)

# Historical scenarios (approximate NSE/Nifty impacts)
SCENARIOS = {
    "COVID-19 Crash (Mar 2020)":         {"shock": -0.38, "vol_mult": 3.5, "description": "Nifty fell ~38% in 40 days"},
    "IL&FS Crisis (Oct 2018)":           {"shock": -0.15, "vol_mult": 2.0, "description": "NBFC liquidity crisis"},
    "Demonetization (Nov 2016)":         {"shock": -0.07, "vol_mult": 1.8, "description": "Nifty dropped ~7% in 2 weeks"},
    "Lehman Brothers (Sep 2008)":        {"shock": -0.55, "vol_mult": 4.0, "description": "Global financial crisis, Nifty −55%"},
    "Dot-com Bust (2000-2001)":          {"shock": -0.40, "vol_mult": 2.5, "description": "Tech bubble burst"},
    "Ukraine War (Feb 2022)":            {"shock": -0.12, "vol_mult": 1.5, "description": "Geopolitical shock"},
    "US Fed Rate Hike Panic (Jun 2022)": {"shock": -0.18, "vol_mult": 2.0, "description": "Inflation + rate hike fears"},
    "Adani Group Selloff (Jan 2023)":    {"shock": -0.06, "vol_mult": 1.3, "description": "Hindenburg report impact"},
    "Custom Scenario":                   {"shock": None,  "vol_mult": None, "description": "User-defined shock"},
}


def tab_stress(prices_df, selected_tickers, weights, ret_method):
    """Stress Testing & Scenario Analysis tab."""

    if prices_df is None or len(selected_tickers) == 0:
        st.warning("⚠️ Load stock data from the sidebar first.")
        return

    available = [t for t in selected_tickers if t in prices_df.columns]
    if not available:
        st.error("No matching ticker data available.")
        return

    px_df = prices_df[available].dropna()
    if len(px_df) < 20:
        st.error("Insufficient data for stress testing.")
        return

    if ret_method == "Log Returns":
        ret_df = np.log(px_df / px_df.shift(1)).dropna()
    else:
        ret_df = px_df.pct_change().dropna()

    w_raw = np.array(weights[:len(available)], dtype=float)
    w     = w_raw / w_raw.sum()
    port_r = portfolio_returns(ret_df, w)

    st.html(
        f'<div style="background:linear-gradient(135deg,#3d0000,#660000);'
        f'border-radius:12px;padding:20px 24px;margin-bottom:16px;{NO_SEL}">'
        f'<span style="font-family:{FH};color:#FFD700;-webkit-text-fill-color:#FFD700;'
        f'font-size:1.5rem;font-weight:700">🔥 Stress Testing & Scenario Analysis</span><br>'
        f'<span style="color:#ADD8E6;-webkit-text-fill-color:#ADD8E6;font-family:{FB};font-size:.9rem">'
        f'Historical crisis scenarios + custom shocks | Portfolio: '
        + " · ".join([f"{t}({w_raw[i]:.0f}%)" for i,t in enumerate(available)])
        + f'</span></div>'
    )

    # ── Scenario selector ────────────────────────────────────────
    section_h("⚡ Select & Customize Scenarios")
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        scenario_name = st.selectbox("Crisis Scenario", list(SCENARIOS.keys()))
    with c2:
        invest = st.number_input("Investment Amount (₹)", value=1000000, step=100000, min_value=10000)
    with c3:
        conf_lv = st.selectbox("Confidence Level", [0.95, 0.99, 0.975], format_func=lambda x: f"{x*100:.1f}%")

    scenario = SCENARIOS[scenario_name]
    if scenario["shock"] is None:
        c_a, c_b, c_c = st.columns(3)
        with c_a:
            custom_shock = st.slider("Portfolio Shock (%)", -70, 20, -20) / 100
        with c_b:
            custom_vol_mult = st.slider("Volatility Multiplier", 1.0, 5.0, 2.0, step=0.5)
        with c_c:
            custom_days = st.slider("Stress Duration (days)", 1, 60, 10)
        shock = custom_shock
        vol_mult = custom_vol_mult
        n_days = custom_days
    else:
        shock    = scenario["shock"]
        vol_mult = scenario["vol_mult"]
        n_days   = 10
        render_ib(f"📌 {scenario_name} — {scenario['description']}", "amber")

    # ── Compute stress metrics ────────────────────────────────────
    port_vol  = port_r.std()
    stress_vol = port_vol * vol_mult
    mu        = port_r.mean()
    alpha     = 1 - conf_lv

    from scipy.stats import norm
    z = norm.ppf(alpha)

    # Stressed VaR (using shocked vol)
    stressed_var  = -(mu + z * stress_vol)
    stressed_cvar = -(mu - stress_vol * norm.pdf(z) / alpha)
    normal_var    = -(mu + z * port_vol)
    normal_cvar   = -(mu - port_vol * norm.pdf(z) / alpha)

    # Capital loss under scenario
    scenario_loss = abs(shock)
    # Per-day shock
    daily_shock   = shock / n_days

    # ── Metrics ───────────────────────────────────────────────────
    m1 = metric_card("Scenario Loss",       f"{shock*100:.1f}%",
                     f"₹{abs(shock)*invest:,.0f}", "#dc3545")
    m2 = metric_card("Normal VaR",          f"{normal_var*100:.3f}%",
                     f"₹{normal_var*invest:,.0f}", "#ADD8E6")
    m3 = metric_card("Stressed VaR",        f"{stressed_var*100:.3f}%",
                     f"₹{stressed_var*invest:,.0f}", "#ff9f43")
    m4 = metric_card("Normal CVaR",         f"{normal_cvar*100:.3f}%",
                     f"₹{normal_cvar*invest:,.0f}", "#a29bfe")
    m5 = metric_card("Stressed CVaR",       f"{stressed_cvar*100:.3f}%",
                     f"₹{stressed_cvar*invest:,.0f}", "#dc3545")
    m6 = metric_card("Volatility Mult",     f"{vol_mult:.1f}×",
                     f"σ: {stress_vol*100:.3f}%/day", "#FFD700")
    st.html(f'<div style="display:grid;grid-template-columns:repeat(6,1fr);gap:9px;margin-bottom:14px">'
            + "".join(f'<div>{m}</div>' for m in [m1,m2,m3,m4,m5,m6]) + '</div>')

    # ── Normal vs Stressed comparison bar ────────────────────────
    section_h("📊 Normal vs Stressed Risk Measures")
    categories = ["VaR", "CVaR", "Scenario Loss"]
    normal_vals  = [normal_var  * 100, normal_cvar  * 100, abs(shock) * 100]
    stressed_vals= [stressed_var* 100, stressed_cvar* 100, abs(shock) * 100]

    fig = go.Figure()
    fig.add_trace(go.Bar(name="Normal Market",  x=categories, y=normal_vals,
                         marker_color="#ADD8E6",
                         text=[f"{v:.3f}%" for v in normal_vals], textposition="outside"))
    fig.add_trace(go.Bar(name="Stressed Market",x=categories, y=stressed_vals,
                         marker_color="#dc3545",
                         text=[f"{v:.3f}%" for v in stressed_vals], textposition="outside"))
    fig.update_layout(**PLOTLY_LAYOUT, barmode="group", height=350,
                      title="Normal vs Stressed VaR / CVaR Comparison",
                      yaxis_title="Risk Measure (%)")
    st.plotly_chart(fig, use_container_width=True)

    # ── Scenario path simulation ──────────────────────────────────
    section_h("📉 Simulated Stress Path")
    n_paths  = 500
    t_arr    = np.arange(n_days + 1)
    sim_paths= np.zeros((n_paths, n_days + 1))
    for i in range(n_paths):
        daily_shocks = np.random.normal(daily_shock, stress_vol, n_days)
        sim_paths[i, 0] = 0
        sim_paths[i, 1:] = np.cumsum(daily_shocks)

    fig2 = go.Figure()
    for i in range(min(200, n_paths)):
        clr = "#dc3545" if sim_paths[i, -1] < shock else "#1a3a5f"
        fig2.add_trace(go.Scatter(x=t_arr, y=sim_paths[i] * 100, mode="lines",
                                  line=dict(color=clr, width=0.5), showlegend=False, opacity=0.3))
    p50 = np.percentile(sim_paths, 50, axis=0) * 100
    p5  = np.percentile(sim_paths, 5,  axis=0) * 100
    p1  = np.percentile(sim_paths, 1,  axis=0) * 100
    fig2.add_trace(go.Scatter(x=t_arr, y=p50, mode="lines", name="Median",
                              line=dict(color="#FFD700", width=2.5)))
    fig2.add_trace(go.Scatter(x=t_arr, y=p5, mode="lines", name="5th Pct",
                              line=dict(color="#ff9f43", width=2, dash="dash")))
    fig2.add_trace(go.Scatter(x=t_arr, y=p1, mode="lines", name="1st Pct",
                              line=dict(color="#dc3545", width=2, dash="dot")))
    fig2.add_hline(y=shock * 100, line_dash="solid", line_color="#FFD700", line_width=2,
                   annotation_text=f"Scenario: {shock*100:.1f}%")
    fig2.update_layout(**PLOTLY_LAYOUT, height=360,
                       title=f"Stress Scenario — {n_days} Day Path Simulation",
                       xaxis_title="Days", yaxis_title="Cumulative Return (%)")
    st.plotly_chart(fig2, use_container_width=True)

    # ── All Scenarios comparison ───────────────────────────────────
    section_h("🌐 All Historical Scenario Comparison")
    scen_names, scen_losses, stressed_vars_all, stressed_cvars_all = [], [], [], []
    for sname, sdata in SCENARIOS.items():
        if sdata["shock"] is None:
            continue
        s_shock  = sdata["shock"]
        s_vmult  = sdata["vol_mult"]
        s_vol    = port_vol * s_vmult
        s_var    = -(mu + z * s_vol)
        s_cvar   = -(mu - s_vol * norm.pdf(z) / alpha)
        scen_names.append(sname.split("(")[0].strip()[:25])
        scen_losses.append(abs(s_shock) * 100)
        stressed_vars_all.append(s_var * 100)
        stressed_cvars_all.append(s_cvar * 100)

    fig3 = go.Figure()
    fig3.add_trace(go.Bar(name="Scenario Loss %", x=scen_names, y=scen_losses,
                          marker_color="#dc3545", opacity=0.85))
    fig3.add_trace(go.Bar(name="Stressed VaR %",  x=scen_names, y=stressed_vars_all,
                          marker_color="#ff9f43", opacity=0.85))
    fig3.add_trace(go.Bar(name="Stressed CVaR %", x=scen_names, y=stressed_cvars_all,
                          marker_color="#FFD700", opacity=0.85))
    fig3.update_layout(**PLOTLY_LAYOUT, barmode="group", height=380,
                       title="Historical Crisis — Scenario Loss vs Stressed VaR/CVaR",
                       xaxis_tickangle=-25, yaxis_title="Loss / Risk (%)",
                       xaxis_title="")
    st.plotly_chart(fig3, use_container_width=True)

    # ── Summary table ─────────────────────────────────────────────
    section_h("📋 Full Scenario Analysis Table")
    rows = []
    for sname, sdata in SCENARIOS.items():
        if sdata["shock"] is None:
            continue
        s_shock = sdata["shock"]
        s_vmult = sdata["vol_mult"]
        s_vol   = port_vol * s_vmult
        s_var   = -(mu + z * s_vol)
        s_cvar  = -(mu - s_vol * norm.pdf(z) / alpha)
        flag = "🔴" if abs(s_shock) > 0.30 else ("🟡" if abs(s_shock) > 0.10 else "🟢")
        rows.append([
            flag + " " + sname.split("(")[0].strip()[:30],
            f"{s_shock*100:.1f}%",
            f"₹{abs(s_shock)*invest:,.0f}",
            f"{s_vmult:.1f}×",
            f"{s_var*100:.3f}%",
            f"{s_cvar*100:.3f}%",
        ])
    st.html(table_html(
        ["Scenario", "Loss %", "₹ Loss", "Vol Mult", "Stressed VaR", "Stressed CVaR"],
        rows
    ))

    render_ib(
        f"🔴 {rt('Severe')} = loss >30% | 🟡 {hl('Moderate')} = 10-30% | 🟢 {gt('Mild')} = <10%  |  "
        f"Basel FRTB requires stressed ES computed over a {hl('12-month stressed period')} (GFC 2008-09 typically used). "
        f"Capital requirement = max(latest ES, 60-day avg ES × multiplier ≥ 1.5).", "purple"
    )
