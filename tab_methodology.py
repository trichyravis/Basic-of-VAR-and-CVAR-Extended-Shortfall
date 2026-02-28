"""tab_methodology.py — Educational reference for VaR / CVaR / ES methods"""
import streamlit as st
from components import (section_h, render_card, ib, render_ib, fml, bdg,
                        table_html, NO_SEL, FH, FB, FM, TXT, hl, gt, rt, lb, mut, p)


def tab_methodology():
    """Educational content on all VaR methods."""

    st.html(
        f'<div style="background:linear-gradient(135deg,#003366,#004d80);'
        f'border-radius:12px;padding:20px 24px;margin-bottom:16px;{NO_SEL}">'
        f'<span style="font-family:{FH};color:#FFD700;-webkit-text-fill-color:#FFD700;'
        f'font-size:1.6rem;font-weight:700">📚 Methodology — VaR / CVaR / ES Reference</span><br>'
        f'<span style="color:#ADD8E6;-webkit-text-fill-color:#ADD8E6;font-family:{FB};font-size:.9rem">'
        f'Complete mathematical reference for risk professionals</span></div>'
    )

    # ── VaR Overview ─────────────────────────────────────────────
    section_h("1️⃣ Value at Risk (VaR) — Overview")
    render_ib(
        f"{hl('Value at Risk (VaR)')} is the maximum loss not exceeded with probability (1-α) "
        f"over a given time horizon. Formally: P(Loss > VaR) = α. For example, a 95% 1-day VaR of 2% "
        f"means there is a 5% chance that the portfolio loses more than 2% in a single day.", "blue"
    )
    st.html(table_html(
        ["Method", "Assumption", "Strengths", "Weaknesses", "Best For"],
        [
            ["Historical Simulation", "Past returns repeat", "No distribution assumption; captures fat tails", "Requires large history; not forward-looking", "Established portfolios"],
            ["Parametric (Normal)", "Returns ~ N(μ, σ²)", "Simple; analytical; fast", "Underestimates tail risk; assumes normality", "Liquid assets"],
            ["Student-t", "Returns ~ t(ν, μ, σ)", "Captures fat tails; fitted dof", "Assumes symmetric distribution", "Equity/FX markets"],
            ["Cornish-Fisher", "Adjusts Normal for skew & kurt", "Fast; higher-moment correction", "Breaks down at extreme skew/kurtosis", "Options portfolios"],
            ["Monte Carlo", "Parametric simulation", "Flexible; handles path dependency", "Computationally intensive; model risk", "Derivatives, complex portfolios"],
            ["EWMA (RiskMetrics)", "Exponentially weighted variance", "Reacts quickly to market shocks", "Assumes normal innovations", "Trading desks"],
            ["GARCH(1,1)", "Conditional heteroskedasticity", "Models volatility clustering", "Parameter estimation risk", "Risk management systems"],
        ]
    ))

    # ── Method formulae ───────────────────────────────────────────
    section_h("2️⃣ Mathematical Formulae")
    
    render_card("Historical Simulation", 
        f'<p style="{TXT}">{hl("Algorithm")}: Sort T historical daily returns in ascending order. VaR = −(α·T)-th quantile.</p>'
        + fml(
            "Let r_(1) ≤ r_(2) ≤ ... ≤ r_(T) be sorted returns\n"
            "VaR_hist(α)  = − r_(⌊αT⌋)\n"
            "CVaR_hist(α) = − (1/⌊αT⌋) Σ_{i=1}^{⌊αT⌋} r_(i)   [average of losses beyond VaR]\n"
            "ES           = CVaR   [identical under continuous distribution]"
        ), "#ADD8E6"
    )

    render_card("Parametric — Normal",
        f'<p style="{TXT}">{hl("Assumes")} returns are i.i.d. Normal with constant mean μ and volatility σ.</p>'
        + fml(
            "VaR_N(α)   = −(μ + z_α · σ)        z_α = Φ⁻¹(α)  [standard normal quantile]\n"
            "CVaR_N(α)  = −(μ − σ · φ(z_α) / α)  φ = standard normal PDF\n\n"
            "Annual:    σ_annual = σ_daily · √252\n"
            "T-day VaR: VaR(T)   = VaR(1) · √T      [Basel √T rule]"
        ), "#FFD700"
    )

    render_card("Parametric — Student-t",
        f'<p style="{TXT}">{hl("Fits")} Student-t distribution via MLE to capture heavy tails. ν = degrees of freedom < Normal when ν < ∞.</p>'
        + fml(
            "Returns ~ t(ν, μ, σ)   where ν = fitted dof\n"
            "VaR_t(α)  = −(μ + t⁻¹(α; ν) · σ)\n"
            "CVaR_t(α) = −μ + σ · t_pdf(t⁻¹(α;ν); ν) / α · (ν + [t⁻¹(α;ν)]²) / (ν − 1)\n\n"
            "As ν → ∞:  t-distribution → Normal distribution\n"
            "Typical equity: ν ≈ 3–6 (fat tails)"
        ), "#64ffda"
    )

    render_card("Cornish-Fisher (Modified VaR)",
        f'<p style="{TXT}">{hl("Adjusts")} the Normal quantile z_α using higher moments (skewness S, excess kurtosis K).</p>'
        + fml(
            "z_CF = z + (z²−1)·S/6 + (z³−3z)·K/24 − (2z³−5z)·S²/36\n\n"
            "VaR_CF(α) = −(μ + z_CF · σ)\n\n"
            "Where:  S = skewness(returns)\n"
            "        K = excess kurtosis(returns)   [= kurtosis − 3]\n"
            "        z = Φ⁻¹(α)   [unadjusted Normal quantile]\n\n"
            "Note: Cornish-Fisher may be non-monotone for extreme skew (|S| > 2). Treat with caution."
        ), "#ff9f43"
    )

    render_card("Monte Carlo VaR",
        f'<p style="{TXT}">{hl("Simulates")} thousands of return scenarios using Cholesky decomposition for correlated assets.</p>'
        + fml(
            "Single Asset:\n"
            "  Simulate r_i ~ N(μ, σ²), i = 1, ..., N_sim\n"
            "  VaR_MC(α) = −Quantile(r_i, α)\n\n"
            "Portfolio (Cholesky):\n"
            "  Σ = L · L'   [Cholesky decomposition of covariance matrix]\n"
            "  z_i ~ N(0, I)\n"
            "  r_sim = z · L' + μ   [correlated scenarios]\n"
            "  r_port = r_sim · w\n"
            "  VaR_MC = −Quantile(r_port, α)"
        ), "#a29bfe"
    )

    render_card("EWMA — RiskMetrics",
        f'<p style="{TXT}">{hl("Exponentially Weighted Moving Average")} gives more weight to recent observations. J.P. Morgan RiskMetrics uses λ=0.94.</p>'
        + fml(
            "σ²(t) = λ · σ²(t-1) + (1-λ) · r²(t-1)   λ ∈ [0,1], typically 0.94\n\n"
            "VaR_EWMA(α) = −(μ + z_α · σ(t))\n\n"
            "Effective lookback ≈ 1/(1-λ) = 16.7 days (at λ=0.94)\n"
            "Half-life        = ln(0.5)/ln(λ) ≈ 11 days (at λ=0.94)\n\n"
            "Advantage: Reacts quickly to volatility shocks vs rolling window"
        ), "#28a745"
    )

    render_card("GARCH(1,1)",
        f'<p style="{TXT}">{hl("Generalised Autoregressive Conditional Heteroskedasticity")} — models time-varying volatility clustering.</p>'
        + fml(
            "Returns:  r_t = μ + ε_t,    ε_t = σ_t · z_t,   z_t ~ N(0,1)\n"
            "Variance: σ²_t = ω + α · ε²(t-1) + β · σ²(t-1)\n\n"
            "Constraints: ω > 0, α ≥ 0, β ≥ 0, α + β < 1  (covariance stationarity)\n"
            "Long-run variance: σ̄² = ω / (1 − α − β)\n"
            "Persistence: α + β (close to 1 → long memory in volatility)\n\n"
            "VaR_GARCH(α) = −(μ + z_α · σ_T+1|T)"
        ), "#dc3545"
    )

    # ── CVaR / ES section ─────────────────────────────────────────
    section_h("3️⃣ CVaR, Expected Shortfall & Extended Metrics")
    render_ib(
        f"{hl('CVaR (Conditional VaR)')} = {hl('ES (Expected Shortfall)')} — the expected loss "
        f"given that the loss exceeds VaR. Coherent risk measure (satisfies subadditivity). "
        f"Preferred over VaR in Basel III/FRTB for trading book capital. "
        f"CVaR always ≥ VaR for same confidence level.", "amber"
    )

    st.html(table_html(
        ["Measure", "Formula", "Interpretation", "Used By"],
        [
            ["Expected Shortfall (ES)", "E[Loss | Loss > VaR]", "Average tail loss", "Basel III FRTB"],
            ["CVaR", "= ES (continuous dist.)", "Conditional tail average", "Risk departments"],
            ["Superquantile", "= ES / CVaR", "Identical to ES", "Academic literature"],
            ["Spectral RM", "Σ φ(i) · r_(i), exp-weighted", "Weights extreme losses more", "Advanced RM"],
            ["Entropic VaR (EVaR)", "min_z {log(MGF(-z·r)) - log(α)} / z", "Upper bound to CVaR", "Robust RM"],
            ["Stressed ES", "ES over worst historical window", "Captures stress scenarios", "FRTB stress testing"],
            ["Range VaR", "VaR(99%) − VaR(95%)", "Tail risk spread", "Model comparison"],
            ["Tail Conditional Expectation", "= ES (continuous)", "Actuarial equivalent", "Insurance"],
        ]
    ))

    # ── Portfolio risk ─────────────────────────────────────────────
    section_h("4️⃣ Portfolio Risk Decomposition")
    render_card("Component & Marginal VaR",
        fml(
            "Portfolio VaR:    VaR_p = z_α · σ_p = z_α · √(w'Σw)\n\n"
            "Marginal VaR_i:  ∂VaR_p/∂w_i = (Σw)_i / σ_p · z_α\n"
            "Component VaR_i: CVaR_i = w_i · Marginal VaR_i\n"
            "Property:         Σ Component VaR_i = Portfolio VaR   [Euler's theorem]\n\n"
            "% Contribution_i: = Component VaR_i / Portfolio VaR × 100\n\n"
            "Diversification Benefit = Σ(w_i · Indiv VaR_i) − Portfolio VaR\n"
            "Diversification Ratio   = Σ(w_i · Indiv VaR_i) / Portfolio VaR ≥ 1"
        ), "#FFD700"
    )

    # ── Backtesting ───────────────────────────────────────────────
    section_h("5️⃣ VaR Backtesting — Kupiec POF Test")
    render_ib(
        f"Backtest compares the number of {hl('exceptions')} (days when actual loss > VaR) "
        f"against the expected number. For 95% VaR over 250 days: expected = 0.05 × 250 = 12.5 exceptions. "
        f"Basel traffic light: 0–4 exceptions (Green), 5–9 (Yellow), ≥10 (Red — capital surcharge).", "purple"
    )
    st.html(fml(
        "H₀: p = α   (exception rate equals expected rate)\n"
        "H₁: p ≠ α\n\n"
        "LR = −2[log L(α; N, n) − log L(p̂; N, n)]\n"
        "   = −2[n·log(α) + (N−n)·log(1−α) − n·log(p̂) − (N−n)·log(1−p̂)]\n\n"
        "p̂ = n/N   (observed exception rate)\n"
        "LR ~ χ²(1)   under H₀\n"
        "Reject H₀ if p-value < 0.05\n\n"
        "Basel: Green Zone: 0–4 exceptions, Yellow: 5–9, Red: ≥ 10 (250 trading days)"
    ))

    # ── Basel III FRTB ───────────────────────────────────────────
    section_h("6️⃣ Basel III / FRTB Capital Requirements")
    st.html(table_html(
        ["Regime", "Metric", "Confidence Level", "Horizon", "Notes"],
        [
            ["Basel II / III", "VaR", "99%", "10 days", "√10 scaling from 1-day"],
            ["Basel III FRTB", "Expected Shortfall (ES)", "97.5%", "10 days", "Replaces VaR for trading book"],
            ["Basel III FRTB", "Stressed ES", "97.5%", "10 days", "Calibrated to stressed period"],
            ["Basel III (ICAAP)", "Stressed VaR", "99%", "10 days", "Additional capital buffer"],
            ["Internal Models", "ES + IMA", "97.5%", "Various", "With model approval"],
            ["SEBI / NSE Margin", "VaR (SPAN)", "99%", "1 day", "For derivatives margining"],
        ]
    ))
    render_ib(
        f"{hl('FRTB Note')} — The Fundamental Review of the Trading Book (FRTB, Basel IV) "
        f"replaces 99% VaR with {hl('97.5% Expected Shortfall')} because ES is a coherent risk measure "
        f"(satisfies subadditivity), captures tail risk better, and penalises liquidity risk through "
        f"Liquidity Horizons (LH) of 10, 20, 40, 60, 120 days for different risk factors.", "gold"
    )

    # ── Key formulae summary ──────────────────────────────────────
    section_h("7️⃣ Quick Reference Summary")
    st.html(fml(
        "═══════════════ VaR QUICK REFERENCE ═══════════════\n\n"
        "Historical:       VaR = −Quantile(r, α)\n"
        "Normal:           VaR = −(μ + Φ⁻¹(α) · σ)\n"
        "Student-t:        VaR = −(μ + t⁻¹(α,ν) · σ)\n"
        "Cornish-Fisher:   VaR = −(μ + z_CF · σ)\n"
        "Monte Carlo:      VaR = −Quantile(simulated returns, α)\n"
        "EWMA:             σ²(t) = λσ²(t-1) + (1-λ)r²(t-1); VaR = −(μ + z_α·σ(t))\n"
        "GARCH(1,1):       σ²(t) = ω + αε²(t-1) + βσ²(t-1); VaR = −(μ + z_α·σ(t))\n\n"
        "CVaR = ES = E[r | r < −VaR]   (average of tail losses)\n\n"
        "Component VaR_i   = w_i · (Σw)_i / σ_p · z_α\n"
        "Marginal VaR_i    = (Σw)_i / σ_p · z_α\n"
        "Incremental VaR_i = VaR(w) − VaR(w without asset i)\n\n"
        "Basel VaR(10d)    = VaR(1d) · √10    [√T rule, i.i.d. assumption]\n"
        "FRTB ES(97.5%)    ≈ VaR(99%) × 1.4   [rough equivalence]"
    ))
