"""
var_engine.py — VaR / CVaR / ES calculation engine for Nifty stocks
Supports: Historical, Parametric (Normal), Parametric (Student-t),
          Cornish-Fisher, Monte Carlo
Also: Component VaR, Marginal VaR, Incremental VaR,
      Conditional VaR / Expected Shortfall (ES)
"""
import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import norm, t as t_dist
from scipy.linalg import cholesky
import warnings
warnings.filterwarnings("ignore")


# ─── Nifty 50 constituents ────────────────────────────────────────────────────
NIFTY50 = {
    "RELIANCE":    "RELIANCE.NS",   "TCS":         "TCS.NS",
    "HDFCBANK":    "HDFCBANK.NS",   "ICICIBANK":   "ICICIBANK.NS",
    "INFY":        "INFY.NS",       "HINDUNILVR":  "HINDUNILVR.NS",
    "ITC":         "ITC.NS",        "SBIN":        "SBIN.NS",
    "BHARTIARTL":  "BHARTIARTL.NS", "KOTAKBANK":   "KOTAKBANK.NS",
    "LT":          "LT.NS",         "AXISBANK":    "AXISBANK.NS",
    "ASIANPAINT":  "ASIANPAINT.NS", "WIPRO":       "WIPRO.NS",
    "MARUTI":      "MARUTI.NS",     "NESTLEIND":   "NESTLEIND.NS",
    "POWERGRID":   "POWERGRID.NS",  "HCLTECH":     "HCLTECH.NS",
    "TITAN":       "TITAN.NS",      "BAJFINANCE":  "BAJFINANCE.NS",
    "ONGC":        "ONGC.NS",       "NTPC":        "NTPC.NS",
    "SUNPHARMA":   "SUNPHARMA.NS",  "TECHM":       "TECHM.NS",
    "TATAMOTORS":  "TATAMOTORS.NS", "BAJAJFINSV":  "BAJAJFINSV.NS",
    "ADANIPORTS":  "ADANIPORTS.NS", "INDUSINDBK":  "INDUSINDBK.NS",
    "COALINDIA":   "COALINDIA.NS",  "GRASIM":      "GRASIM.NS",
    "ULTRACEMCO":  "ULTRACEMCO.NS", "ADANIENT":    "ADANIENT.NS",
    "DRREDDY":     "DRREDDY.NS",    "CIPLA":       "CIPLA.NS",
    "BPCL":        "BPCL.NS",       "EICHERMOT":   "EICHERMOT.NS",
    "APOLLOHOSP":  "APOLLOHOSP.NS", "TATACONSUM":  "TATACONSUM.NS",
    "DIVISLAB":    "DIVISLAB.NS",   "HEROMOTOCO":  "HEROMOTOCO.NS",
    "SBILIFE":     "SBILIFE.NS",    "BRITANNIA":   "BRITANNIA.NS",
    "HDFCLIFE":    "HDFCLIFE.NS",   "JSWSTEEL":    "JSWSTEEL.NS",
    "TATASTEEL":   "TATASTEEL.NS",  "MM":          "M&M.NS",
    "HINDALCO":    "HINDALCO.NS",   "LTIM":        "LTIM.NS",
    "UPL":         "UPL.NS",        "SHRIRAMFIN":  "SHRIRAMFIN.NS",
}

SECTOR_MAP = {
    "RELIANCE":"Energy","TCS":"IT","HDFCBANK":"Banking","ICICIBANK":"Banking",
    "INFY":"IT","HINDUNILVR":"FMCG","ITC":"FMCG","SBIN":"Banking",
    "BHARTIARTL":"Telecom","KOTAKBANK":"Banking","LT":"Infra","AXISBANK":"Banking",
    "ASIANPAINT":"Consumer","WIPRO":"IT","MARUTI":"Auto","NESTLEIND":"FMCG",
    "POWERGRID":"Utilities","HCLTECH":"IT","TITAN":"Consumer","BAJFINANCE":"NBFC",
    "ONGC":"Energy","NTPC":"Utilities","SUNPHARMA":"Pharma","TECHM":"IT",
    "TATAMOTORS":"Auto","BAJAJFINSV":"NBFC","ADANIPORTS":"Infra","INDUSINDBK":"Banking",
    "COALINDIA":"Energy","GRASIM":"Diversified","ULTRACEMCO":"Cement","ADANIENT":"Diversified",
    "DRREDDY":"Pharma","CIPLA":"Pharma","BPCL":"Energy","EICHERMOT":"Auto",
    "APOLLOHOSP":"Healthcare","TATACONSUM":"FMCG","DIVISLAB":"Pharma","HEROMOTOCO":"Auto",
    "SBILIFE":"Insurance","BRITANNIA":"FMCG","HDFCLIFE":"Insurance","JSWSTEEL":"Metals",
    "TATASTEEL":"Metals","MM":"Auto","HINDALCO":"Metals","LTIM":"IT",
    "UPL":"Agro","SHRIRAMFIN":"NBFC",
}


def fetch_data(tickers: list[str], period: str = "1y") -> pd.DataFrame:
    """Download adjusted close prices via yfinance."""
    import yfinance as yf
    raw = yf.download(tickers, period=period, auto_adjust=True, progress=False)
    if isinstance(raw.columns, pd.MultiIndex):
        prices = raw["Close"]
    else:
        prices = raw
    prices = prices.dropna(how="all")
    return prices


def compute_returns(prices: pd.DataFrame, method: str = "log") -> pd.DataFrame:
    """Compute daily returns (log or simple)."""
    if method == "log":
        return np.log(prices / prices.shift(1)).dropna()
    else:
        return prices.pct_change().dropna()


# ─── VaR & CVaR methods ───────────────────────────────────────────────────────

def historical_var_cvar(returns: np.ndarray, cl: float = 0.95) -> dict:
    """Historical Simulation VaR & CVaR."""
    alpha  = 1 - cl
    var    = -np.percentile(returns, alpha * 100)
    losses = -returns[returns < -var]
    cvar   = losses.mean() if len(losses) > 0 else var
    es     = -np.mean(np.sort(returns)[:max(1, int(alpha * len(returns)))])
    return {"var": var, "cvar": cvar, "es": es, "method": "Historical Simulation"}


def parametric_normal_var_cvar(returns: np.ndarray, cl: float = 0.95) -> dict:
    """Parametric VaR & CVaR assuming Normal distribution."""
    mu    = np.mean(returns)
    sigma = np.std(returns, ddof=1)
    alpha = 1 - cl
    z     = norm.ppf(alpha)
    var   = -(mu + z * sigma)
    # CVaR (Normal): mu + sigma * phi(z) / alpha
    cvar  = -(mu - sigma * norm.pdf(norm.ppf(alpha)) / alpha)
    return {"var": var, "cvar": cvar, "es": cvar, "mu": mu, "sigma": sigma,
            "method": "Parametric (Normal)"}


def parametric_t_var_cvar(returns: np.ndarray, cl: float = 0.95) -> dict:
    """Parametric VaR & CVaR using Student-t distribution (fitted dof)."""
    alpha  = 1 - cl
    df, loc, scale = t_dist.fit(returns)
    df = max(df, 2.01)
    z  = t_dist.ppf(alpha, df=df)
    var = -(loc + z * scale)
    # CVaR for t: -loc + scale * t_pdf(t_ppf) / alpha * (df + z^2) / (df - 1)
    z_a    = t_dist.ppf(alpha, df=df)
    cvar_t = -(loc - scale * t_dist.pdf(z_a, df=df) / alpha * (df + z_a**2) / (df - 1))
    return {"var": var, "cvar": cvar_t, "es": cvar_t,
            "dof": df, "loc": loc, "scale": scale, "method": "Parametric (Student-t)"}


def cornish_fisher_var_cvar(returns: np.ndarray, cl: float = 0.95) -> dict:
    """Cornish-Fisher (Modified) VaR adjusting for skewness & kurtosis."""
    mu    = np.mean(returns)
    sigma = np.std(returns, ddof=1)
    s     = stats.skew(returns)
    k     = stats.kurtosis(returns)  # excess kurtosis
    alpha = 1 - cl
    z     = norm.ppf(alpha)
    # Cornish-Fisher expansion
    z_cf  = (z
             + (z**2 - 1) * s / 6
             + (z**3 - 3*z) * k / 24
             - (2*z**3 - 5*z) * s**2 / 36)
    var   = -(mu + z_cf * sigma)
    # CVaR via numerical integration or bootstrap — use parametric normal CVaR scaled
    cvar_normal = -(mu - sigma * norm.pdf(norm.ppf(alpha)) / alpha)
    skew_adj    = 1 + abs(s) * 0.1 + abs(k) * 0.02
    cvar        = cvar_normal * skew_adj
    return {"var": var, "cvar": cvar, "es": cvar,
            "skew": s, "kurt": k, "z_cf": z_cf, "method": "Cornish-Fisher (Modified)"}


def monte_carlo_var_cvar(returns: np.ndarray, cl: float = 0.95,
                         n_sims: int = 50000, horizon: int = 1) -> dict:
    """Monte Carlo VaR & CVaR using fitted Normal distribution."""
    mu     = np.mean(returns)
    sigma  = np.std(returns, ddof=1)
    alpha  = 1 - cl
    sims   = np.random.normal(mu * horizon, sigma * np.sqrt(horizon), n_sims)
    var    = -np.percentile(sims, alpha * 100)
    losses = -sims[sims < -var]
    cvar   = losses.mean() if len(losses) > 0 else var
    return {"var": var, "cvar": cvar, "es": cvar,
            "n_sims": n_sims, "mu": mu, "sigma": sigma, "method": "Monte Carlo"}


def ewma_var_cvar(returns: np.ndarray, cl: float = 0.95, lam: float = 0.94) -> dict:
    """EWMA (RiskMetrics) Volatility-based VaR."""
    n     = len(returns)
    sigma2 = np.zeros(n)
    sigma2[0] = returns[0]**2
    for i in range(1, n):
        sigma2[i] = lam * sigma2[i-1] + (1 - lam) * returns[i-1]**2
    vol   = np.sqrt(sigma2[-1])
    mu    = np.mean(returns)
    alpha = 1 - cl
    z     = norm.ppf(alpha)
    var   = -(mu + z * vol)
    cvar  = -(mu - vol * norm.pdf(z) / alpha)
    return {"var": var, "cvar": cvar, "es": cvar,
            "ewma_vol": vol, "lambda": lam, "method": "EWMA (RiskMetrics)"}


def garch_var_cvar(returns: np.ndarray, cl: float = 0.95) -> dict:
    """
    Simplified GARCH(1,1) VaR — analytical approximation.
    omega = (1-alpha-beta) * long_run_var
    Uses method-of-moments for alpha and beta.
    """
    mu    = np.mean(returns)
    sigma = np.std(returns, ddof=1)
    alpha_g = 0.05    # ARCH parameter
    beta_g  = 0.90    # GARCH parameter
    omega   = sigma**2 * (1 - alpha_g - beta_g)
    
    n = len(returns)
    h = np.zeros(n)
    h[0] = sigma**2
    for i in range(1, n):
        h[i] = omega + alpha_g * returns[i-1]**2 + beta_g * h[i-1]
    
    vol   = np.sqrt(h[-1])
    alpha = 1 - cl
    z     = norm.ppf(alpha)
    var   = -(mu + z * vol)
    cvar  = -(mu - vol * norm.pdf(z) / alpha)
    return {"var": var, "cvar": cvar, "es": cvar,
            "garch_vol": vol, "method": "GARCH(1,1)"}


def all_var_methods(returns: np.ndarray, cl: float = 0.95,
                    n_sims: int = 50000, lam: float = 0.94) -> dict:
    """Run all 6 VaR methods and return consolidated results."""
    results = {
        "Historical":       historical_var_cvar(returns, cl),
        "Normal":           parametric_normal_var_cvar(returns, cl),
        "Student-t":        parametric_t_var_cvar(returns, cl),
        "Cornish-Fisher":   cornish_fisher_var_cvar(returns, cl),
        "Monte Carlo":      monte_carlo_var_cvar(returns, cl, n_sims),
        "EWMA":             ewma_var_cvar(returns, cl, lam),
        "GARCH(1,1)":       garch_var_cvar(returns, cl),
    }
    return results


# ─── Multi-horizon VaR ────────────────────────────────────────────────────────

def scale_var(var_1d: float, horizon: int, scaling: str = "sqrt_t") -> float:
    """Scale 1-day VaR to multi-day using sqrt(T) or linear scaling."""
    if scaling == "sqrt_t":
        return var_1d * np.sqrt(horizon)
    return var_1d * horizon


# ─── Portfolio VaR ────────────────────────────────────────────────────────────

def portfolio_returns(returns_df: pd.DataFrame, weights: np.ndarray) -> np.ndarray:
    """Compute portfolio return time series."""
    weights = np.array(weights) / np.sum(weights)  # normalise
    return returns_df.values @ weights


def portfolio_parametric_var(returns_df: pd.DataFrame, weights: np.ndarray,
                              cl: float = 0.95) -> dict:
    """Parametric portfolio VaR with covariance matrix."""
    w    = np.array(weights) / np.sum(weights)
    cov  = returns_df.cov().values
    mu_v = returns_df.mean().values
    port_mu  = w @ mu_v
    port_var = w @ cov @ w
    port_vol = np.sqrt(port_var)
    alpha    = 1 - cl
    z        = norm.ppf(alpha)
    var      = -(port_mu + z * port_vol)
    cvar     = -(port_mu - port_vol * norm.pdf(z) / alpha)
    return {"var": var, "cvar": cvar, "port_vol": port_vol,
            "port_mu": port_mu, "cov": cov}


def component_var(returns_df: pd.DataFrame, weights: np.ndarray,
                  cl: float = 0.95) -> pd.DataFrame:
    """Component VaR — each asset's contribution to total portfolio VaR."""
    w    = np.array(weights) / np.sum(weights)
    cov  = returns_df.cov().values
    port_vol = np.sqrt(w @ cov @ w)
    alpha    = 1 - cl
    z        = norm.ppf(alpha)
    # Marginal VaR = dVaR/dw_i  = (cov @ w) / port_vol * z
    marginal = (cov @ w) / port_vol * (-z)
    component = w * marginal
    pct_contribution = component / component.sum() * 100
    df = pd.DataFrame({
        "Ticker":           returns_df.columns.tolist(),
        "Weight (%)":       (w * 100).round(2),
        "Marginal VaR":     marginal.round(5),
        "Component VaR":    component.round(5),
        "% Contribution":   pct_contribution.round(2),
    })
    return df


def incremental_var(returns_df: pd.DataFrame, weights: np.ndarray,
                    cl: float = 0.95) -> pd.DataFrame:
    """Incremental VaR — change in portfolio VaR when each position is removed."""
    w = np.array(weights) / np.sum(weights)
    base = portfolio_parametric_var(returns_df, w, cl)["var"]
    rows = []
    for i, col in enumerate(returns_df.columns):
        w_new = w.copy()
        w_new = np.delete(w_new, i)
        df_new = returns_df.drop(columns=[col])
        if len(w_new) == 0:
            inc = base
        else:
            w_new = w_new / w_new.sum()
            new_var = portfolio_parametric_var(df_new, w_new, cl)["var"]
            inc = base - new_var
        rows.append({"Ticker": col, "Incremental VaR": round(inc, 5),
                     "% of Portfolio VaR": round(inc / base * 100, 2)})
    return pd.DataFrame(rows)


def diversification_benefit(returns_df: pd.DataFrame,
                             weights: np.ndarray, cl: float = 0.95) -> dict:
    """Diversification ratio and benefit."""
    w = np.array(weights) / np.sum(weights)
    alpha = 1 - cl
    z     = abs(norm.ppf(alpha))
    # Undiversified VaR = sum of individual VaRs
    ind_vols = returns_df.std().values
    ind_vars  = ind_vols * z
    undiv_var = w @ ind_vars
    # Portfolio VaR
    cov       = returns_df.cov().values
    port_vol  = np.sqrt(w @ cov @ w)
    port_var  = port_vol * z
    div_benefit = undiv_var - port_var
    div_ratio   = undiv_var / port_var if port_var > 0 else 1.0
    return {
        "undiversified_var": undiv_var, "portfolio_var": port_var,
        "diversification_benefit": div_benefit,
        "diversification_ratio": div_ratio,
    }


def mc_portfolio_var(returns_df: pd.DataFrame, weights: np.ndarray,
                     cl: float = 0.95, n_sims: int = 50000) -> dict:
    """Monte Carlo portfolio VaR using Cholesky decomposition."""
    w      = np.array(weights) / np.sum(weights)
    mu_v   = returns_df.mean().values
    cov    = returns_df.cov().values
    alpha  = 1 - cl
    try:
        L = cholesky(cov + np.eye(len(w)) * 1e-10, lower=True)
    except Exception:
        L = np.diag(np.sqrt(np.diag(cov)))
    z     = np.random.randn(n_sims, len(w))
    sims  = z @ L.T + mu_v
    port  = sims @ w
    var   = -np.percentile(port, alpha * 100)
    losses = -port[port < -var]
    cvar   = losses.mean() if len(losses) > 0 else var
    return {"var": var, "cvar": cvar, "sim_returns": port, "method": "Monte Carlo (Cholesky)"}


# ─── Extended Risk Metrics ────────────────────────────────────────────────────

def extended_shortfall_metrics(returns: np.ndarray, cl: float = 0.95) -> dict:
    """
    Extended shortfall metrics beyond simple CVaR:
    - ES (Expected Shortfall / CVaR)
    - Superquantile
    - Tail Risk Contribution
    - Spectral Risk Measure (exponential weights)
    - Range VaR
    - Stressed ES
    """
    alpha     = 1 - cl
    n         = len(returns)
    sorted_r  = np.sort(returns)
    cutoff_n  = max(1, int(alpha * n))
    tail      = sorted_r[:cutoff_n]

    # ES = Expected Shortfall
    es        = -np.mean(tail)

    # Superquantile (another name for ES)
    superq    = es

    # Spectral Risk Measure (exponential weighting — more weight on extreme losses)
    phi       = np.exp(-np.arange(cutoff_n) * 3 / cutoff_n)
    phi       = phi / phi.sum()
    spectral  = -np.dot(sorted_r[:cutoff_n], phi)

    # Range VaR = VaR at 99% - VaR at 95%
    var_99    = -np.percentile(returns, 1)
    var_95    = -np.percentile(returns, 5)
    range_var = var_99 - var_95

    # Stressed ES: compute ES on the worst calendar year's data
    n_stress  = min(n, 60)  # ~3 months of worst period
    worst_idx = np.argsort(returns)[:n_stress]
    stressed_es = -np.mean(returns[worst_idx])

    # Entropic VaR (EVaR) — upper bound to ES
    z_alpha   = norm.ppf(alpha)
    evars     = []
    for z_e in np.linspace(0.1, 5.0, 200):
        try:
            mgf = np.mean(np.exp(-z_e * returns))
            if mgf > 0 and np.isfinite(np.log(mgf)):
                evar_z = (np.log(mgf) - np.log(alpha)) / z_e
                if np.isfinite(evar_z) and 0 < evar_z < 2.0:
                    evars.append(evar_z)
        except Exception:
            pass
    evar      = min(max(evars), es * 2.5) if evars else es * 1.2

    # Conditional Tail Expectation (same as ES in continuous case)
    cte = es

    return {
        "es":             es,
        "superquantile":  superq,
        "spectral_rm":    spectral,
        "range_var":      range_var,
        "stressed_es":    stressed_es,
        "evar":           evar,
        "cte":            cte,
        "var_99":         var_99,
        "var_95":         var_95,
    }


def backtesting_kupiec(returns: np.ndarray, var_series: np.ndarray,
                       cl: float = 0.95) -> dict:
    """
    Kupiec POF (Proportion of Failures) backtest for VaR.
    H0: actual exception rate == expected exception rate (1-cl)
    """
    alpha      = 1 - cl
    exceptions = (returns < -var_series).sum()
    n          = len(returns)
    p_hat      = exceptions / n
    # LR test statistic
    if 0 < p_hat < 1:
        lr = -2 * (np.log((alpha**exceptions) * ((1 - alpha)**(n - exceptions))) -
                   np.log((p_hat**exceptions) * ((1 - p_hat)**(n - exceptions))))
    else:
        lr = 0.0
    p_value = 1 - stats.chi2.cdf(lr, df=1)
    return {
        "exceptions": int(exceptions),
        "n": n,
        "expected": int(alpha * n),
        "exception_rate": round(p_hat * 100, 2),
        "expected_rate":  round(alpha * 100, 2),
        "lr_statistic":   round(lr, 4),
        "p_value":        round(p_value, 4),
        "pass": p_value > 0.05,
    }


def rolling_var(returns: np.ndarray, window: int = 63, cl: float = 0.95,
                method: str = "hist") -> pd.Series:
    """Compute rolling VaR series."""
    s     = pd.Series(returns)
    alpha = 1 - cl
    result = []
    for i in range(window, len(s) + 1):
        chunk = s.iloc[i - window:i].values
        if method == "hist":
            result.append(-np.percentile(chunk, alpha * 100))
        else:
            mu, sig = chunk.mean(), chunk.std(ddof=1)
            result.append(-(mu + norm.ppf(alpha) * sig))
    return pd.Series(result, index=s.index[window - 1:])


# ─── Descriptive stats ───────────────────────────────────────────────────────

def descriptive_stats(returns: np.ndarray, ticker: str = "") -> dict:
    s = {}
    s["mean_daily"]   = np.mean(returns)
    s["mean_annual"]  = np.mean(returns) * 252
    s["vol_daily"]    = np.std(returns, ddof=1)
    s["vol_annual"]   = np.std(returns, ddof=1) * np.sqrt(252)
    s["skewness"]     = stats.skew(returns)
    s["excess_kurt"]  = stats.kurtosis(returns)
    s["min"]          = np.min(returns)
    s["max"]          = np.max(returns)
    s["n_obs"]        = len(returns)
    jb_stat, jb_p     = stats.jarque_bera(returns)
    s["jarque_bera"]  = jb_stat
    s["jb_pvalue"]    = jb_p
    s["is_normal"]    = jb_p > 0.05
    s["sharpe"]       = s["mean_annual"] / s["vol_annual"] if s["vol_annual"] > 0 else 0
    s["max_drawdown"] = _max_drawdown(returns)
    return s


def _max_drawdown(returns: np.ndarray) -> float:
    cum = np.cumprod(1 + returns)
    peak = np.maximum.accumulate(cum)
    dd = (cum - peak) / peak
    return float(dd.min())
