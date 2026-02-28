"""components.py — Mountain Path HTML building blocks (st.html + inline styles)"""
import streamlit as st

NO_SEL = "user-select:none;-webkit-user-select:none"
FH     = "'Playfair Display',serif"
FB     = "'Source Sans Pro',sans-serif"
FM     = "'JetBrains Mono',monospace"
TXT    = f"color:#e6f1ff;font-family:{FB};line-height:1.65;-webkit-text-fill-color:#e6f1ff"

def _g(c, t): return f'<span style="color:{c};-webkit-text-fill-color:{c};font-weight:600">{t}</span>'
def hl(t):    return _g("#FFD700", t)
def gt(t):    return _g("#28a745", t)
def rt(t):    return _g("#dc3545", t)
def lb(t):    return _g("#ADD8E6", t)
def mut(t):   return _g("#8892b0", t)
def acc(t):   return _g("#64ffda", t)
def amb(t):   return _g("#ff9f43", t)

def p(text): return f'<p style="{TXT};margin-bottom:6px">{text}</p>'

def render_card(title, body_html, color="#FFD700"):
    st.html(
        f'<div style="background:#112240;border:1px solid #1e3a5f;border-radius:12px;'
        f'padding:22px;margin-bottom:16px;{NO_SEL}">'
        f'<h2 style="font-family:{FH};font-size:1.25rem;color:{color};'
        f'-webkit-text-fill-color:{color};border-bottom:1px solid #1e3a5f;'
        f'padding-bottom:8px;margin:0 0 14px">{title}</h2>'
        f'{body_html}</div>'
    )

def ib(content, variant="blue"):
    borders = {
        "blue":  ("#ADD8E6","rgba(0,51,102,.6)"),
        "gold":  ("#FFD700","rgba(255,215,0,.1)"),
        "green": ("#28a745","rgba(40,167,69,.12)"),
        "red":   ("#dc3545","rgba(220,53,69,.12)"),
        "amber": ("#ff9f43","rgba(255,159,67,.12)"),
        "purple":("#a29bfe","rgba(162,155,254,.12)"),
        "teal":  ("#00cec9","rgba(0,206,201,.12)"),
    }
    bc, bg = borders.get(variant, borders["blue"])
    return (f'<div style="background:{bg};border-left:4px solid {bc};border-radius:8px;'
            f'padding:12px 15px;margin:8px 0;{TXT};{NO_SEL}">{content}</div>')

def render_ib(content, variant="blue"):
    st.html(ib(content, variant))

def fml(text):
    return (f'<div style="background:#0d1f3a;border-left:4px solid #FFD700;border-radius:6px;'
            f'padding:12px 16px;margin:8px 0;font-family:{FM};font-size:.85rem;'
            f'color:#64ffda;-webkit-text-fill-color:#64ffda;line-height:1.8;'
            f'white-space:pre-wrap;overflow-x:auto;{NO_SEL}">{text}</div>')

def bdg(text, variant="blue"):
    cols = {
        "blue":  ("#004d80","#fff"),  "gold":  ("#FFD700","#0a1628"),
        "green": ("#28a745","#fff"),  "red":   ("#dc3545","#fff"),
        "amber": ("#ff9f43","#0a1628"),"purple":("#a29bfe","#0a1628"),
        "teal":  ("#00cec9","#0a1628"),
    }
    bg, fg = cols.get(variant, cols["blue"])
    return (f'<span style="background:{bg};color:{fg};-webkit-text-fill-color:{fg};'
            f'display:inline-block;padding:2px 10px;border-radius:20px;font-size:.76rem;'
            f'font-weight:700;margin:2px 2px;font-family:{FB};{NO_SEL}">{text}</span>')

def metric_card(label, value, sublabel="", color="#FFD700"):
    return (f'<div style="background:#0d1f3a;border:1px solid #1e3a5f;border-radius:10px;'
            f'padding:16px;text-align:center;{NO_SEL}">'
            f'<div style="color:#8892b0;-webkit-text-fill-color:#8892b0;'
            f'font-family:{FB};font-size:.78rem;font-weight:600;margin-bottom:5px">{label}</div>'
            f'<div style="font-family:{FM};font-size:1.45rem;font-weight:700;'
            f'color:{color};-webkit-text-fill-color:{color}">{value}</div>'
            + (f'<div style="color:#8892b0;-webkit-text-fill-color:#8892b0;font-family:{FB};'
               f'font-size:.74rem;margin-top:3px">{sublabel}</div>' if sublabel else "")
            + f'</div>')

def table_html(headers, rows):
    ths = "".join(
        f'<th style="background:#003366;color:#FFD700;-webkit-text-fill-color:#FFD700;'
        f'padding:9px 12px;text-align:left;font-weight:600;font-family:{FB};font-size:.84rem">{h}</th>'
        for h in headers
    )
    trs = ""
    for i, row in enumerate(rows):
        bg  = "rgba(0,51,102,.2)" if i % 2 == 0 else "transparent"
        tds = "".join(
            f'<td style="padding:8px 12px;border-bottom:1px solid #1e3a5f;background:{bg};'
            f'color:#e6f1ff;-webkit-text-fill-color:#e6f1ff;font-family:{FB};font-size:.84rem">{c}</td>'
            for c in row
        )
        trs += f'<tr>{tds}</tr>'
    return (f'<table style="width:100%;border-collapse:collapse;margin:10px 0;'
            f'font-size:.84rem;{NO_SEL}"><tr>{ths}</tr>{trs}</table>')

def section_h(title, color="#ADD8E6"):
    st.html(f'<h3 style="font-family:{FH};color:{color};-webkit-text-fill-color:{color};'
            f'font-size:1.05rem;margin:16px 0 8px 0;{NO_SEL}">{title}</h3>')

def progress_bar(value, max_val=1.0, color="#FFD700", height=8):
    pct = min(100, max(0, value / max_val * 100))
    return (f'<div style="background:#1e3a5f;border-radius:{height}px;height:{height}px;overflow:hidden;{NO_SEL}">'
            f'<div style="background:{color};width:{pct:.1f}%;height:100%;border-radius:{height}px;'
            f'transition:width .5s ease"></div></div>')

def hero_header(title, subtitle, icon="📊"):
    st.html(
        f'<div style="background:linear-gradient(135deg,#003366,#004d80,#005c99);'
        f'border-radius:14px;padding:28px 32px;margin-bottom:18px;'
        f'border:1px solid #1e5a8a;{NO_SEL}">'
        f'<div style="font-size:2.5rem;margin-bottom:8px">{icon}</div>'
        f'<h1 style="font-family:{FH};color:#FFD700;-webkit-text-fill-color:#FFD700;'
        f'font-size:1.9rem;font-weight:700;margin:0 0 6px">{title}</h1>'
        f'<p style="color:#ADD8E6;-webkit-text-fill-color:#ADD8E6;font-family:{FB};'
        f'font-size:.95rem;margin:0">{subtitle}</p>'
        f'</div>'
    )

def footer():
    st.html(
        f'<div style="background:#0d1f3a;border-top:1px solid #1e3a5f;border-radius:10px;'
        f'padding:16px 24px;margin-top:30px;text-align:center;{NO_SEL}">'
        f'<p style="color:#8892b0;-webkit-text-fill-color:#8892b0;font-family:{FB};'
        f'font-size:.80rem;margin:0">'
        f'<span style="color:#FFD700;-webkit-text-fill-color:#FFD700;font-weight:700">'
        f'The Mountain Path – World of Finance</span> &nbsp;|&nbsp; '
        f'<span style="color:#e6f1ff;-webkit-text-fill-color:#e6f1ff">'
        f'Prof. V. Ravichandran</span> &nbsp;|&nbsp; '
        f'28+ Years Corporate Finance &amp; Banking Experience &nbsp;|&nbsp; '
        f'10+ Years Academic Excellence &nbsp;|&nbsp; '
        f'<a href="https://www.linkedin.com/in/trichyravis" target="_blank" '
        f'style="color:#FFD700;-webkit-text-fill-color:#FFD700;text-decoration:none">'
        f'LinkedIn</a> &nbsp;|&nbsp; '
        f'<a href="https://github.com/trichyravis" target="_blank" '
        f'style="color:#FFD700;-webkit-text-fill-color:#FFD700;text-decoration:none">'
        f'GitHub</a>'
        f'</p></div>'
    )

def two_col(l, r):
    return (f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;margin:8px 0">'
            f'<div>{l}</div><div>{r}</div></div>')

def three_col(a, b, c):
    return (f'<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;margin:8px 0">'
            f'<div>{a}</div><div>{b}</div><div>{c}</div></div>')

def four_col(a, b, c, d):
    return (f'<div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:10px;margin:8px 0">'
            f'<div>{a}</div><div>{b}</div><div>{c}</div><div>{d}</div></div>')

def five_col(a, b, c, d, e):
    return (f'<div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr 1fr;gap:10px;margin:8px 0">'
            f'<div>{a}</div><div>{b}</div><div>{c}</div><div>{d}</div><div>{e}</div></div>')

def var_result_card(method, var_pct, cvar_pct, color="#FFD700", icon="📐"):
    return (
        f'<div style="background:#0d1f3a;border:1px solid #1e3a5f;border-radius:10px;'
        f'padding:16px 18px;{NO_SEL}">'
        f'<div style="font-size:1.3rem;margin-bottom:4px">{icon}</div>'
        f'<div style="color:#8892b0;-webkit-text-fill-color:#8892b0;font-family:{FB};'
        f'font-size:.75rem;font-weight:600;text-transform:uppercase;margin-bottom:6px">{method}</div>'
        f'<div style="font-family:{FM};font-size:1.3rem;font-weight:700;'
        f'color:{color};-webkit-text-fill-color:{color}">{var_pct}</div>'
        f'<div style="color:#8892b0;-webkit-text-fill-color:#8892b0;font-family:{FB};font-size:.73rem;margin-top:2px">'
        f'VaR &nbsp;|&nbsp; <span style="color:#ff9f43;-webkit-text-fill-color:#ff9f43">{cvar_pct}</span> CVaR</div>'
        f'</div>'
    )
