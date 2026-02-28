"""styles.py — Mountain Path CSS for Nifty VaR / CVaR / ES App"""
import streamlit as st

C = {
    "dark":   "#0a1628", "card":   "#112240", "blue":   "#003366",
    "mid":    "#004d80", "gold":   "#FFD700", "lb":     "#ADD8E6",
    "grn":    "#28a745", "red":    "#dc3545", "txt":    "#e6f1ff",
    "mut":    "#8892b0", "acc":    "#64ffda", "amber":  "#ff9f43",
    "purple": "#a29bfe", "teal":   "#00cec9",
}

def inject_css():
    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Source+Sans+Pro:wght@300;400;600&family=JetBrains+Mono:wght@400;600&display=swap');

.stApp {{
    background: linear-gradient(135deg,#0d1b2a,#1a2d45,#0f2340) !important;
    font-family: 'Source Sans Pro', sans-serif !important;
}}
#MainMenu, footer, header {{ visibility: hidden; }}
.block-container {{ padding-top: 0.4rem !important; max-width: 1400px; }}

.stTabs [data-baseweb="tab-list"] {{
    background: {C['card']} !important;
    border-radius: 10px; padding: 5px; gap: 4px;
    border: 1px solid #1e3a5f; flex-wrap: wrap;
}}
.stTabs [data-baseweb="tab"] {{
    background: transparent !important;
    color: {C['mut']} !important;
    font-family: 'Source Sans Pro', sans-serif !important;
    font-weight: 600 !important; font-size: .84rem !important;
    border-radius: 7px !important; padding: 7px 14px !important;
    border: none !important; transition: all .2s !important;
}}
.stTabs [data-baseweb="tab"]:hover {{ color: {C['gold']} !important; background: rgba(0,77,128,.3) !important; }}
.stTabs [aria-selected="true"] {{
    background: {C['blue']} !important; color: {C['gold']} !important;
    border: 1px solid {C['gold']} !important;
}}
.stTabs [data-baseweb="tab-border"] {{ display:none !important; }}
.stTabs [data-baseweb="tab-panel"] {{ padding-top: 12px !important; }}

div[data-testid="stMetric"] {{
    background: {C['card']} !important;
    border: 1px solid #1e3a5f !important; border-radius: 10px !important;
    padding: 14px 16px !important;
}}
div[data-testid="stMetric"] label {{ color: {C['lb']} !important; font-weight: 600 !important; font-size:.82rem !important; }}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {{
    color: {C['gold']} !important;
    font-family: 'JetBrains Mono', monospace !important; font-size: 1.3rem !important;
}}
div[data-testid="stMetric"] [data-testid="stMetricDelta"] {{ font-size:.78rem !important; }}

.stSelectbox label, .stSlider label, .stRadio label,
.stNumberInput label, .stMultiSelect label, .stTextInput label {{
    color: {C['lb']} !important; font-weight: 600 !important;
}}
.stSelectbox [data-baseweb="select"] > div,
.stMultiSelect [data-baseweb="select"] > div {{
    background: {C['card']} !important; border-color: #1e3a5f !important; color: {C['txt']} !important;
}}
.stNumberInput input, .stTextInput input {{
    background: {C['card']} !important; border-color: #1e3a5f !important;
    color: {C['txt']} !important;
}}
.stSlider [data-testid="stSlider"] div[role="slider"] {{
    background: {C['gold']} !important;
}}

div[data-testid="stSidebar"] {{
    background: #0d1f3a !important;
    border-right: 1px solid #1e3a5f;
}}
div[data-testid="stSidebar"] * {{ color: {C['txt']} !important; }}

.stButton > button {{
    background: linear-gradient(135deg,{C['blue']},{C['mid']}) !important;
    color: {C['gold']} !important;
    border: 1px solid {C['gold']} !important;
    font-family: 'Source Sans Pro', sans-serif !important;
    font-weight: 700 !important; border-radius: 8px !important;
    padding: 8px 20px !important; transition: all .2s !important;
}}
.stButton > button:hover {{
    background: linear-gradient(135deg,{C['mid']},{C['blue']}) !important;
    box-shadow: 0 4px 15px rgba(255,215,0,.3) !important;
}}

div[data-testid="stExpander"] {{
    background: {C['card']} !important;
    border: 1px solid #1e3a5f !important; border-radius: 10px !important;
}}

.stDataFrame {{ background: {C['card']} !important; }}
.stDataFrame thead th {{ background: {C['blue']} !important; color: {C['gold']} !important; }}
</style>
""", unsafe_allow_html=True)
