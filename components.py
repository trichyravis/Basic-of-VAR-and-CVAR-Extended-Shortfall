"""
components.py — Mountain Path design system for Nifty VaR App v2.
All HTML via st.html() with 100% inline styles + user-select:none.
Matches Linear Regression app design framework exactly.
"""
import streamlit as st

NO_SEL = "user-select:none;-webkit-user-select:none"
FH     = "'Playfair Display',serif"
FB     = "'Source Sans Pro',sans-serif"
FM     = "'JetBrains Mono',monospace"
TXT    = f"color:#e6f1ff;font-family:{FB};line-height:1.65;-webkit-text-fill-color:#e6f1ff"

# ── Colour shortcuts ──────────────────────────────────────────────────────────
def _g(c, t): return f'<span style="color:{c};-webkit-text-fill-color:{c};font-weight:600">{t}</span>'
def hl(t):    return _g("#FFD700", t)
def gt(t):    return _g("#28a745", t)
def rt(t):    return _g("#dc3545", t)
def lb(t):    return _g("#ADD8E6", t)
def mut(t):   return _g("#8892b0", t)
def acc(t):   return _g("#64ffda", t)
def org(t):   return _g("#ff9f43", t)
def pur(t):   return _g("#a29bfe", t)
def teal(t):  return _g("#00cec9", t)
def p(text):  return f'<p style="{TXT};margin-bottom:7px">{text}</p>'

# ── Info-box colours ──────────────────────────────────────────────────────────
_IB = {
    "blue":   ("rgba(0,51,102,0.6)",    "#ADD8E6"),
    "gold":   ("rgba(255,215,0,0.13)",  "#FFD700"),
    "green":  ("rgba(40,167,69,0.2)",   "#28a745"),
    "red":    ("rgba(220,53,69,0.2)",   "#dc3545"),
    "amber":  ("rgba(255,159,67,0.15)", "#ff9f43"),
    "orange": ("rgba(255,159,67,0.15)", "#ff9f43"),
    "purple": ("rgba(162,155,254,0.15)","#a29bfe"),
    "teal":   ("rgba(0,206,201,0.15)",  "#00cec9"),
}
_BADGE = {
    "blue":   ("#004d80","#ffffff"), "gold":   ("#FFD700","#0a1628"),
    "green":  ("#28a745","#ffffff"), "red":    ("#dc3545","#ffffff"),
    "amber":  ("#ff9f43","#0a1628"), "orange": ("#ff9f43","#0a1628"),
    "purple": ("#a29bfe","#0a1628"), "teal":   ("#00cec9","#0a1628"),
}

# ── Core components ───────────────────────────────────────────────────────────

def render_card(title: str, body_html: str, color: str = "#FFD700"):
    st.html(
        f'<div style="background:#112240;border:1px solid #1e3a5f;border-radius:10px;'
        f'padding:22px;margin-bottom:18px;{NO_SEL}">'
        f'<h2 style="font-family:{FH};font-size:1.3rem;color:{color};'
        f'-webkit-text-fill-color:{color};border-bottom:1px solid #1e3a5f;'
        f'padding-bottom:8px;margin:0 0 14px 0">{title}</h2>'
        f'{body_html}</div>'
    )

def ib(content, variant="blue"):
    bg, bc = _IB.get(variant, _IB["blue"])
    return (f'<div style="background:{bg};border-left:4px solid {bc};border-radius:8px;'
            f'padding:13px 15px;margin:10px 0;{TXT};{NO_SEL}">{content}</div>')

def render_ib(content, variant="blue"): st.html(ib(content, variant))

def fml(content):
    return (f'<div style="background:#0d1f3a;border-left:4px solid #FFD700;border-radius:6px;'
            f'padding:13px 17px;margin:10px 0;font-family:{FM};font-size:.87rem;'
            f'color:#64ffda;-webkit-text-fill-color:#64ffda;line-height:1.85;'
            f'white-space:pre-wrap;overflow-x:auto;{NO_SEL}">{content}</div>')

def bdg(text, variant="blue"):
    bg, fg = _BADGE.get(variant, _BADGE["blue"])
    return (f'<span style="background:{bg};color:{fg};-webkit-text-fill-color:{fg};'
            f'display:inline-block;padding:2px 10px;border-radius:20px;font-size:.77rem;'
            f'font-weight:700;margin:2px;font-family:{FB};{NO_SEL}">{text}</span>')

def section_h(title, color="#ADD8E6"):
    st.html(
        f'<h3 style="font-family:{FH};color:{color};-webkit-text-fill-color:{color};'
        f'font-size:1.1rem;margin:18px 0 8px 0;border-left:3px solid #FFD700;'
        f'padding-left:10px;{NO_SEL}">{title}</h3>'
    )

def section_heading(title, color="#ADD8E6"):
    section_h(title, color)

# ── Metric cards ──────────────────────────────────────────────────────────────

def metric_card(label, value, sublabel="", color="#FFD700"):
    return (
        f'<div style="background:#0d1f3a;border:1px solid #1e3a5f;border-radius:10px;'
        f'padding:16px;text-align:center;{NO_SEL}">'
        f'<div style="color:#8892b0;-webkit-text-fill-color:#8892b0;'
        f'font-family:{FB};font-size:.78rem;font-weight:600;margin-bottom:5px">{label}</div>'
        f'<div style="font-family:{FM};font-size:1.4rem;font-weight:700;'
        f'color:{color};-webkit-text-fill-color:{color}">{value}</div>'
        + (f'<div style="color:#8892b0;-webkit-text-fill-color:#8892b0;font-family:{FB};'
           f'font-size:.74rem;margin-top:3px">{sublabel}</div>' if sublabel else "")
        + f'</div>'
    )

def hero_metric(label, value, sublabel="", trend="", color="#FFD700"):
    """Large gradient metric card for top-of-section KPIs."""
    trend_html = ""
    if trend == "up":
        trend_html = f'<span style="color:#28a745;-webkit-text-fill-color:#28a745;font-size:.85rem"> ▲</span>'
    elif trend == "down":
        trend_html = f'<span style="color:#dc3545;-webkit-text-fill-color:#dc3545;font-size:.85rem"> ▼</span>'
    return (
        f'<div style="background:linear-gradient(135deg,#0d1f3a,#112240);'
        f'border:1px solid #1e3a5f;border-top:3px solid {color};border-radius:10px;'
        f'padding:18px 16px;text-align:center;{NO_SEL}">'
        f'<div style="color:#8892b0;-webkit-text-fill-color:#8892b0;'
        f'font-family:{FB};font-size:.78rem;font-weight:600;margin-bottom:6px;'
        f'text-transform:uppercase;letter-spacing:.5px">{label}</div>'
        f'<div style="font-family:{FM};font-size:1.6rem;font-weight:700;'
        f'color:{color};-webkit-text-fill-color:{color}">{value}{trend_html}</div>'
        + (f'<div style="color:#8892b0;-webkit-text-fill-color:#8892b0;font-family:{FB};'
           f'font-size:.76rem;margin-top:4px">{sublabel}</div>' if sublabel else "")
        + '</div>'
    )

def stat_box(label, value, variant="blue"):
    bg, bc = _IB.get(variant, _IB["blue"])
    val_col = {"blue":"#ADD8E6","gold":"#FFD700","green":"#28a745","red":"#dc3545",
               "amber":"#ff9f43","orange":"#ff9f43","purple":"#a29bfe","teal":"#00cec9"}.get(variant,"#ADD8E6")
    return (
        f'<div style="background:{bg};border:1px solid {bc};border-radius:8px;padding:14px 16px;{NO_SEL}">'
        f'<div style="color:#8892b0;-webkit-text-fill-color:#8892b0;font-size:.78rem;font-family:{FB};margin-bottom:4px">{label}</div>'
        f'<div style="color:{val_col};-webkit-text-fill-color:{val_col};font-family:{FM};font-size:1.3rem;font-weight:700">{value}</div>'
        f'</div>'
    )

# ── VaR result card ───────────────────────────────────────────────────────────
def var_result_card(method, var_pct, cvar_pct, color="#FFD700", icon="📐"):
    return (
        f'<div style="background:#0d1f3a;border:1px solid {color}40;border-radius:10px;'
        f'border-top:3px solid {color};padding:16px 14px;{NO_SEL}">'
        f'<div style="font-size:1.2rem;margin-bottom:4px">{icon}</div>'
        f'<div style="color:#8892b0;-webkit-text-fill-color:#8892b0;font-family:{FB};'
        f'font-size:.72rem;font-weight:700;text-transform:uppercase;margin-bottom:6px;'
        f'letter-spacing:.4px">{method}</div>'
        f'<div style="font-family:{FM};font-size:1.35rem;font-weight:700;'
        f'color:{color};-webkit-text-fill-color:{color}">{var_pct}</div>'
        f'<div style="color:#8892b0;-webkit-text-fill-color:#8892b0;font-family:{FB};font-size:.72rem;margin-top:3px">'
        f'VaR &nbsp;|&nbsp; <span style="color:#ff9f43;-webkit-text-fill-color:#ff9f43">{cvar_pct}</span> CVaR'
        f'</div></div>'
    )

# ── Tables ────────────────────────────────────────────────────────────────────
def table_html(headers, rows, stripe=True):
    ths = "".join(
        f'<th style="background:#003366;color:#FFD700;-webkit-text-fill-color:#FFD700;'
        f'padding:9px 12px;text-align:left;font-weight:600;font-family:{FB};font-size:.84rem">{h}</th>'
        for h in headers
    )
    trs = ""
    for i, row in enumerate(rows):
        bg = "rgba(0,51,102,.18)" if (stripe and i % 2 == 0) else "transparent"
        tds = "".join(
            f'<td style="padding:8px 12px;border-bottom:1px solid #1e3a5f;background:{bg};'
            f'color:#e6f1ff;-webkit-text-fill-color:#e6f1ff;font-family:{FB};font-size:.84rem">{c}</td>'
            for c in row
        )
        trs += f'<tr>{tds}</tr>'
    return (f'<table style="width:100%;border-collapse:collapse;margin:12px 0;{NO_SEL}">'
            f'<tr>{ths}</tr>{trs}</table>')

# ── Layout helpers ────────────────────────────────────────────────────────────
def two_col(l, r):
    return (f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin:10px 0">'
            f'<div>{l}</div><div>{r}</div></div>')

def three_col(a, b, c):
    return (f'<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:14px;margin:10px 0">'
            f'<div>{a}</div><div>{b}</div><div>{c}</div></div>')

def four_col(a, b, c, d):
    return (f'<div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:12px;margin:10px 0">'
            f'<div>{a}</div><div>{b}</div><div>{c}</div><div>{d}</div></div>')

def five_col(a, b, c, d, e):
    return (f'<div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr 1fr;gap:10px;margin:10px 0">'
            f'<div>{a}</div><div>{b}</div><div>{c}</div><div>{d}</div><div>{e}</div></div>')

def six_col(*args):
    inner = "".join(f'<div>{a}</div>' for a in args)
    return f'<div style="display:grid;grid-template-columns:{"1fr "*len(args)};gap:9px;margin:10px 0">{inner}</div>'

def steps_html(steps):
    rows = ""
    for i, (title, body) in enumerate(steps, 1):
        rows += (
            f'<div style="display:flex;gap:12px;margin-bottom:12px;align-items:flex-start;{NO_SEL}">'
            f'<div style="background:#FFD700;color:#0a1628;-webkit-text-fill-color:#0a1628;'
            f'border-radius:50%;min-width:28px;height:28px;display:flex;align-items:center;'
            f'justify-content:center;font-weight:700;font-size:.85rem;font-family:{FB}">{i}</div>'
            f'<div style="{TXT};flex:1">'
            f'<span style="color:#ADD8E6;-webkit-text-fill-color:#ADD8E6;font-weight:600">{title}</span><br>'
            f'<span style="color:#e6f1ff;-webkit-text-fill-color:#e6f1ff">{body}</span>'
            f'</div></div>'
        )
    return rows

def progress_bar(label, value, max_val=1.0, color="#FFD700", height=8):
    pct = min(100, max(0, value / max_val * 100)) if max_val > 0 else 0
    return (
        f'<div style="{NO_SEL};margin:6px 0">'
        f'<div style="display:flex;justify-content:space-between;margin-bottom:4px">'
        f'<span style="color:#8892b0;-webkit-text-fill-color:#8892b0;font-size:.78rem;font-family:{FB}">{label}</span>'
        f'<span style="color:{color};-webkit-text-fill-color:{color};font-size:.78rem;font-family:{FM};font-weight:600">{pct:.0f}%</span>'
        f'</div>'
        f'<div style="background:#1e3a5f;border-radius:{height}px;height:{height}px;overflow:hidden">'
        f'<div style="background:{color};width:{pct:.1f}%;height:100%;border-radius:{height}px;transition:width .5s ease"></div>'
        f'</div></div>'
    )

# ── App-level header & footer ─────────────────────────────────────────────────
def app_header(title, subtitle, badges=None):
    """Full-width hero header matching LR app style."""
    badge_html = ""
    if badges:
        badge_html = '<div style="display:flex;justify-content:center;gap:10px;margin-top:12px;flex-wrap:wrap">'
        for text, variant in badges:
            bg, fg = _BADGE.get(variant, _BADGE["blue"])
            bdr = {"blue":"#1e3a5f","gold":"#FFD700","green":"#28a745","red":"#dc3545",
                   "amber":"#ff9f43","orange":"#ff9f43","purple":"#a29bfe","teal":"#00cec9"}.get(variant,"#1e3a5f")
            badge_html += (
                f'<span style="background:{bg}22;color:{bg if variant not in ["blue"] else fg};'
                f'-webkit-text-fill-color:{bg if variant not in ["blue"] else fg};'
                f'padding:3px 13px;border-radius:20px;font-size:.78rem;font-family:{FB};'
                f'border:1px solid {bdr}">{text}</span>'
            )
        badge_html += '</div>'
    st.html(
        f'<div style="text-align:center;padding:28px 20px 18px;'
        f'border-bottom:2px solid #FFD700;margin-bottom:24px;{NO_SEL}">'
        f'<div style="font-family:{FH};font-size:2.2rem;color:#FFD700;'
        f'-webkit-text-fill-color:#FFD700;letter-spacing:1px;margin-bottom:6px;font-weight:700">'
        f'{title}</div>'
        f'<div style="color:#8892b0;-webkit-text-fill-color:#8892b0;'
        f'font-family:{FB};font-size:1rem;margin-bottom:4px">{subtitle}</div>'
        f'<div style="color:#ADD8E6;-webkit-text-fill-color:#ADD8E6;'
        f'font-family:{FB};font-size:0.85rem;font-style:italic">'
        f'The Mountain Path – World of Finance &nbsp;|&nbsp; Prof. V. Ravichandran</div>'
        f'{badge_html}</div>'
    )

def tab_banner(title, subtitle, color_from="#003366", color_to="#004d80"):
    """Per-tab gradient banner."""
    st.html(
        f'<div style="background:linear-gradient(135deg,{color_from},{color_to});'
        f'border-radius:12px;padding:20px 24px;margin-bottom:16px;{NO_SEL}">'
        f'<div style="font-family:{FH};color:#FFD700;-webkit-text-fill-color:#FFD700;'
        f'font-size:1.55rem;font-weight:700;margin-bottom:4px">{title}</div>'
        f'<div style="color:#ADD8E6;-webkit-text-fill-color:#ADD8E6;font-family:{FB};font-size:.9rem">'
        f'{subtitle}</div></div>'
    )

def footer():
    st.html(
        f'<div style="text-align:center;padding:18px;color:#8892b0;-webkit-text-fill-color:#8892b0;'
        f'font-family:{FB};font-size:.84rem;border-top:1px solid #1e3a5f;'
        f'margin-top:28px;line-height:1.9;{NO_SEL}">'
        f'<span style="color:#FFD700;-webkit-text-fill-color:#FFD700;font-weight:700">'
        f'The Mountain Path – World of Finance</span><br>'
        f'<a href="https://www.linkedin.com/in/trichyravis" target="_blank" '
        f'style="color:#FFD700;-webkit-text-fill-color:#FFD700;text-decoration:none">LinkedIn</a>'
        f' &nbsp;|&nbsp; '
        f'<a href="https://github.com/trichyravis" target="_blank" '
        f'style="color:#FFD700;-webkit-text-fill-color:#FFD700;text-decoration:none">GitHub</a><br>'
        f'<span style="color:#8892b0;-webkit-text-fill-color:#8892b0">'
        f'Prof. V. Ravichandran &nbsp;|&nbsp; '
        f'28+ Years Corporate Finance &amp; Banking Experience &nbsp;|&nbsp; '
        f'10+ Years Academic Excellence</span></div>'
    )
