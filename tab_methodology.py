"""tab_methodology.py — Educational VaR / CVaR / ES reference  (v2 redesign)"""
import streamlit as st
from components import (
    section_h, render_card, ib, render_ib, fml, bdg,
    table_html, tab_banner, steps_html, two_col, three_col,
    NO_SEL, FH, FB, FM, TXT, hl, gt, rt, lb, org, pur, acc, p
)


def tab_methodology():

    tab_banner(
        "📚 Methodology — VaR / CVaR / ES Reference",
        "Complete mathematical reference for risk professionals · Basel III / FRTB · Backtesting"
    )

    # ── 1. VaR Overview ───────────────────────────────────────────────────
    section_h("1️⃣ Value at Risk — Overview & Method Comparison")
    render_ib(
        f"{hl('Value at Risk (VaR)')} is the maximum loss not exceeded with probability (1−α) "
        f"over a given time horizon. Formally: P(Loss > VaR) = α. "
        f"For example, a {hl('95% 1-day VaR of 2%')} means there is a 5% chance the portfolio "
        f"loses more than 2% in a single day. VaR is the industry standard for market risk "
        f"measurement but has limitations — it does not capture tail losses beyond the threshold.",
        "blue"
    )
    st.html(table_html(
        ["Method", "Assumption", "Strengths", "Weaknesses", "Best For"],
        [
            ["Historical Simulation", "Past returns repeat",
             "No distribution assumption; captures fat tails",
             "Needs large history; not forward-looking", "Established portfolios"],
            ["Parametric (Normal)", "Returns ~ N(μ, σ²)",
             "Analytical; simple; fast",
             "Underestimates tail risk; assumes normality", "Liquid assets"],
            ["Student-t", "Returns ~ t(ν, μ, σ)",
             "Captures fat tails; fitted dof",
             "Symmetric distribution assumption", "Equity / FX markets"],
            ["Cornish-Fisher", "Normal adjusted for skew & kurtosis",
             "Fast; higher-moment correction",
             "Breaks down at extreme skew", "Options portfolios"],
            ["Monte Carlo", "Parametric simulation",
             "Flexible; path-dependent payoffs",
             "Computationally intensive; model risk", "Derivatives, complex portfolios"],
            ["EWMA (RiskMetrics)", "Exp. weighted variance",
             "Reacts quickly to market shocks",
             "Normal innovations assumed", "Trading desks"],
            ["GARCH(1,1)", "Conditional heteroskedasticity",
             "Models volatility clustering",
             "Parameter estimation risk", "Risk management systems"],
        ]
    ))

    # ── 2. Formulae ───────────────────────────────────────────────────────
    section_h("2️⃣ Mathematical Formulae")

    render_card("📊 Historical Simulation",
        p(f"{hl('Algorithm')}: Sort T historical daily returns ascending. VaR = −(α·T)-th quantile.")
        + fml(
            "Let r_(1) ≤ r_(2) ≤ … ≤ r_(T) be sorted returns\n"
            "VaR_hist(α)  = − r_(⌊αT⌋)\n"
            "CVaR_hist(α) = − (1/⌊αT⌋) Σ_{i=1}^{⌊αT⌋} r_(i)   [tail average]\n"
            "ES           = CVaR  (identical under continuous distribution)"
        ), "#ADD8E6"
    )

    render_card("📈 Parametric — Normal",
        p(f"{hl('Assumes')} returns are i.i.d. Normal with constant mean μ and volatility σ.")
        + fml(
            "VaR_N(α)   = −(μ + z_α · σ)         z_α = Φ⁻¹(α)  [standard normal quantile]\n"
            "CVaR_N(α)  = −(μ − σ · φ(z_α) / α)   φ = standard normal PDF\n\n"
            "Annual:    σ_annual = σ_daily · √252\n"
            "T-day VaR: VaR(T)   = VaR(1) · √T       [Basel √T rule]"
        ), "#FFD700"
    )

    render_card("📉 Parametric — Student-t",
        p(f"{hl('Fits')} Student-t distribution via MLE to capture heavy tails. ν = degrees of freedom.")
        + fml(
            "Returns ~ t(ν, μ, σ)   ν = fitted dof\n"
            "VaR_t(α)  = −(μ + t⁻¹(α; ν) · σ)\n"
            "CVaR_t(α) = −μ + σ · t_pdf(t⁻¹(α;ν); ν) / α · (ν + [t⁻¹(α;ν)]²) / (ν − 1)\n\n"
            "As ν → ∞:   t-distribution → Normal distribution\n"
            "Typical equity markets: ν ≈ 3–6  (fat tails)"
        ), "#64ffda"
    )

    render_card("🌀 Cornish-Fisher (Modified VaR)",
        p(f"{hl('Adjusts')} Normal quantile using higher moments: skewness S, excess kurtosis K.")
        + fml(
            "z_CF = z + (z²−1)·S/6 + (z³−3z)·K/24 − (2z³−5z)·S²/36\n\n"
            "VaR_CF(α) = −(μ + z_CF · σ)\n\n"
            "Where:  S = skewness(returns)\n"
            "        K = excess kurtosis(returns)  [= kurtosis − 3]\n"
            "        z = Φ⁻¹(α)  [unadjusted Normal quantile]\n\n"
            "Note: CF may be non-monotone for extreme skew (|S| > 2). Use with caution."
        ), "#ff9f43"
    )

    render_card("🎲 Monte Carlo VaR",
        p(f"{hl('Simulates')} thousands of return scenarios using Cholesky decomposition.")
        + fml(
            "Single Asset:\n"
            "  Simulate r_i ~ N(μ, σ²), i = 1, …, N_sim\n"
            "  VaR_MC(α) = −Quantile(r_i, α)\n\n"
            "Portfolio (Cholesky):\n"
            "  Σ = L · L'   [Cholesky decomposition of covariance matrix]\n"
            "  z_i ~ N(0, I)\n"
            "  r_sim = z · L' + μ   [correlated scenarios]\n"
            "  r_port = r_sim · w\n"
            "  VaR_MC = −Quantile(r_port, α)"
        ), "#a29bfe"
    )

    render_card("⚡ EWMA — RiskMetrics",
        p(f"{hl('Exponentially Weighted Moving Average')} — J.P. Morgan RiskMetrics uses λ=0.94.")
        + fml(
            "σ²(t) = λ · σ²(t-1) + (1-λ) · r²(t-1)    λ ∈ [0,1], typically 0.94\n\n"
            "VaR_EWMA(α) = −(μ + z_α · σ(t))\n\n"
            "Effective lookback ≈ 1/(1-λ) = 16.7 days  (at λ=0.94)\n"
            "Half-life        = ln(0.5)/ln(λ) ≈ 11 days (at λ=0.94)\n\n"
            "Advantage: Reacts faster to volatility shocks vs rolling window"
        ), "#28a745"
    )

    render_card("🔥 GARCH(1,1)",
        p(f"{hl('Generalised Autoregressive Conditional Heteroskedasticity')} — models volatility clustering.")
        + fml(
            "Returns:  r_t = μ + ε_t,   ε_t = σ_t · z_t,  z_t ~ N(0,1)\n"
            "Variance: σ²_t = ω + α · ε²(t-1) + β · σ²(t-1)\n\n"
            "Constraints: ω > 0, α ≥ 0, β ≥ 0, α+β < 1  (covariance stationarity)\n"
            "Long-run variance: σ̄² = ω / (1 − α − β)\n"
            "Persistence: α+β (close to 1 → long memory in volatility)\n\n"
            "VaR_GARCH(α) = −(μ + z_α · σ_{T+1|T})"
        ), "#dc3545"
    )

    # ── 3. CVaR / ES ──────────────────────────────────────────────────────
    section_h("3️⃣ CVaR / Expected Shortfall & Extended Metrics")
    render_ib(
        f"{hl('CVaR')} = {hl('ES')} (Expected Shortfall) — the expected loss given the loss exceeds VaR. "
        f"Coherent risk measure (satisfies subadditivity). Preferred over VaR in Basel III/FRTB for "
        f"trading-book capital. CVaR always ≥ VaR for the same confidence level.",
        "amber"
    )
    st.html(table_html(
        ["Measure", "Formula", "Interpretation", "Used By"],
        [
            ["Expected Shortfall (ES)", "E[Loss | Loss > VaR]", "Average tail loss", "Basel III FRTB"],
            ["CVaR", "= ES (continuous distribution)", "Conditional tail average", "Risk departments"],
            ["Superquantile", "= ES", "Another name for ES", "Academic literature"],
            ["Spectral RM", "Σ φ(i)·r_(i), exp-weighted", "Weights extreme losses more", "Advanced RM"],
            ["Entropic VaR", "min_z {log MGF(−z·r) − log α}/z", "Upper bound to CVaR", "Robust RM"],
            ["Stressed ES", "ES over worst historical window", "Captures stress regimes", "FRTB stress testing"],
            ["Range VaR", "VaR(99%) − VaR(95%)", "Tail risk spread", "Model comparison"],
            ["Tail Cond. Expectation", "= ES (continuous)", "Actuarial equivalent", "Insurance"],
        ]
    ))

    # ── 4. Portfolio Risk ─────────────────────────────────────────────────
    section_h("4️⃣ Portfolio Risk Decomposition")
    render_card("Component & Marginal VaR",
        fml(
            "Portfolio VaR:     VaR_p = z_α · σ_p = z_α · √(w'Σw)\n\n"
            "Marginal VaR_i:    ∂VaR_p/∂w_i = (Σw)_i / σ_p · z_α\n"
            "Component VaR_i:   CVaR_i = w_i · Marginal VaR_i\n"
            "Property:          Σ Component VaR_i = Portfolio VaR   [Euler's theorem]\n\n"
            "% Contribution_i:  = Component VaR_i / Portfolio VaR × 100\n\n"
            "Diversification Benefit = Σ(w_i · Indiv VaR_i) − Portfolio VaR\n"
            "Diversification Ratio   = Σ(w_i · Indiv VaR_i) / Portfolio VaR ≥ 1"
        ), "#FFD700"
    )

    # ── 5. Backtesting ────────────────────────────────────────────────────
    section_h("5️⃣ VaR Backtesting — Kupiec POF Test")
    render_ib(
        f"Backtest compares {hl('exceptions')} (days when actual loss > VaR) against the expected number. "
        f"For 95% VaR over 250 days: expected = 0.05 × 250 = 12.5 exceptions. "
        f"Basel traffic light: {gt('0–4 exceptions (Green)')}, {hl('5–9 (Yellow)')}, {rt('≥10 (Red — capital surcharge)')}.",
        "purple"
    )
    st.html(fml(
        "H₀: p = α   (exception rate = expected rate)\n"
        "H₁: p ≠ α\n\n"
        "LR = −2[log L(α; N, n) − log L(p̂; N, n)]\n"
        "   = −2[n·log(α) + (N−n)·log(1−α) − n·log(p̂) − (N−n)·log(1−p̂)]\n\n"
        "p̂ = n/N   (observed exception rate)\n"
        "LR ~ χ²(1) under H₀\n"
        "Reject H₀ if p-value < 0.05\n\n"
        "Basel zones: 🟢 Green: 0–4 exceptions | 🟡 Yellow: 5–9 | 🔴 Red: ≥10  (250 trading days)"
    ))

    # ── 6. Basel III / FRTB ───────────────────────────────────────────────
    section_h("6️⃣ Basel III / FRTB Capital Requirements")
    st.html(table_html(
        ["Regime", "Metric", "Confidence Level", "Horizon", "Notes"],
        [
            ["Basel II / III", "VaR", "99%", "10 days", "√10 scaling from 1-day"],
            ["Basel III FRTB", "Expected Shortfall (ES)", "97.5%", "10 days", "Replaces VaR for trading book"],
            ["Basel III FRTB", "Stressed ES", "97.5%", "10 days", "Calibrated to stressed period"],
            ["Basel III (ICAAP)", "Stressed VaR", "99%", "10 days", "Additional capital buffer"],
            ["Internal Models (IMA)", "ES + DRC", "97.5%", "Various", "With model approval"],
            ["SEBI / NSE Margin", "VaR (SPAN)", "99%", "1 day", "For derivatives margining"],
        ]
    ))
    render_ib(
        f"{hl('FRTB Note')} — The Fundamental Review of the Trading Book replaces 99% VaR with "
        f"{hl('97.5% Expected Shortfall')} because ES is a coherent risk measure (satisfies subadditivity), "
        f"captures tail risk better, and penalises liquidity risk through Liquidity Horizons (LH) of "
        f"10, 20, 40, 60, 120 days for different risk factor classes.",
        "gold"
    )

    # ── 7. Quick Reference ────────────────────────────────────────────────
    section_h("7️⃣ Quick Reference — All Formulae at a Glance")
    render_card("Master Formula Sheet", fml(
        "═══════════════ VaR QUICK REFERENCE ═══════════════\n\n"
        "Historical:       VaR = −Quantile(r, α)\n"
        "Normal:           VaR = −(μ + Φ⁻¹(α) · σ)\n"
        "Student-t:        VaR = −(μ + t⁻¹(α,ν) · σ)\n"
        "Cornish-Fisher:   VaR = −(μ + z_CF · σ)\n"
        "Monte Carlo:      VaR = −Quantile(simulated returns, α)\n"
        "EWMA:             σ²(t) = λσ²(t-1) + (1-λ)r²(t-1);  VaR = −(μ + z_α·σ(t))\n"
        "GARCH(1,1):       σ²(t) = ω + αε²(t-1) + βσ²(t-1);  VaR = −(μ + z_α·σ(t))\n\n"
        "CVaR = ES = E[r | r < −VaR]   (average of tail losses)\n\n"
        "Component VaR_i   = w_i · (Σw)_i / σ_p · z_α\n"
        "Marginal VaR_i    = (Σw)_i / σ_p · z_α\n"
        "Incremental VaR_i = VaR(w) − VaR(w without asset i)\n\n"
        "Basel VaR(10d)    = VaR(1d) · √10    [√T rule, i.i.d. assumption]\n"
        "FRTB ES(97.5%)    ≈ VaR(99%) × 1.4   [rough equivalence]\n\n"
        "Diversification Ratio = Σ(w_i·VaR_i) / Portfolio VaR ≥ 1"
    ), "#ADD8E6")

    # ── 8. Step-by-step implementation ───────────────────────────────────
    section_h("8️⃣ Implementation Workflow")
    st.html(
        '<div style="background:#112240;border:1px solid #1e3a5f;border-radius:10px;padding:22px;margin-bottom:18px">'
        + steps_html([
            ("Collect Price Data",         "Download daily adjusted closing prices (≥252 trading days recommended for robustness)"),
            ("Compute Returns",            "Log returns: r_t = ln(P_t / P_{t-1}). Simple returns: r_t = (P_t − P_{t-1}) / P_{t-1}"),
            ("Descriptive Statistics",     "Compute μ, σ, skewness, kurtosis, Jarque-Bera test for normality"),
            ("Choose Confidence Level",    "95% for internal RM, 99% for Basel II/III, 97.5% for FRTB ES"),
            ("Compute VaR / CVaR",         "Apply all 7 methods. Cross-validate results — divergence signals fat tails or regime shifts"),
            ("Scale to Horizon",           "T-day VaR = 1-day VaR × √T (assumes i.i.d.; use GARCH for time-varying vol)"),
            ("Backtest with Kupiec POF",   "Compare exception rate to expected rate. p < 0.05 → model misspecification"),
            ("Stress Test",                "Apply historical crisis shocks (COVID-19, GFC). Compute stressed VaR and ES"),
            ("Report Capital Requirement", "Basel: max(VaR × 3, VaR_60day_avg × 3.5). FRTB: max(ES, 60d avg ES × multiplier ≥ 1.5)"),
        ])
        + '</div>'
    )
