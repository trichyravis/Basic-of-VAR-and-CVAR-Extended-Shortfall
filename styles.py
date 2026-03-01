"""styles.py — Mountain Path CSS for Nifty VaR / CVaR / ES App v2"""
import streamlit as st

def inject_css():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Source+Sans+Pro:wght@300;400;600&family=JetBrains+Mono:wght@400;600&display=swap');

.stApp { background: linear-gradient(135deg,#1a2332,#243447,#2a3f5f) !important; font-family:'Source Sans Pro',sans-serif !important; }
#MainMenu,footer,header { visibility:hidden; }
.block-container { padding-top:1rem !important; max-width:1300px; }

.stTabs [data-baseweb="tab-list"] { background:#112240 !important; border-radius:8px; padding:4px; gap:4px; border:1px solid #1e3a5f; flex-wrap:wrap; }
.stTabs [data-baseweb="tab"] { background:transparent !important; color:#8892b0 !important; font-family:'Source Sans Pro',sans-serif !important; font-weight:600 !important; font-size:.88rem !important; border-radius:6px !important; padding:8px 16px !important; border:none !important; transition:all .25s !important; }
.stTabs [data-baseweb="tab"]:hover { color:#FFD700 !important; background:rgba(0,77,128,.3) !important; }
.stTabs [aria-selected="true"] { background:#003366 !important; color:#FFD700 !important; border:1px solid #FFD700 !important; }
.stTabs [data-baseweb="tab-border"] { display:none !important; }
.stTabs [data-baseweb="tab-panel"] { padding-top:14px !important; }

div[data-testid="stMetric"] { background:#112240 !important; border:1px solid #1e3a5f !important; border-radius:8px !important; padding:14px !important; }
div[data-testid="stMetric"] label { color:#ADD8E6 !important; font-weight:600 !important; font-size:.82rem !important; }
div[data-testid="stMetric"] [data-testid="stMetricValue"] { color:#FFD700 !important; font-family:'JetBrains Mono',monospace !important; font-size:1.3rem !important; }
div[data-testid="stMetric"] [data-testid="stMetricDelta"] { color:#ADD8E6 !important; font-size:.78rem !important; }

.stSelectbox label,.stSlider label,.stRadio label,.stNumberInput label,.stMultiSelect label { color:#ADD8E6 !important; font-weight:600 !important; }
.stSelectbox [data-baseweb="select"]>div,.stMultiSelect [data-baseweb="select"]>div { background:#112240 !important; border-color:#1e3a5f !important; color:#e6f1ff !important; }
.stSelectbox [data-baseweb="select"] span,.stMultiSelect span { color:#e6f1ff !important; }
.stRadio div[role="radiogroup"] label span { color:#e6f1ff !important; }
.stNumberInput input,.stTextInput input { background:#112240 !important; color:#e6f1ff !important; border-color:#1e3a5f !important; }
.stButton button { background:#003366 !important; color:#FFD700 !important; border:2px solid #FFD700 !important; font-weight:700 !important; border-radius:6px !important; transition:all .2s !important; }
.stButton button:hover { background:#004d80 !important; box-shadow:0 4px 15px rgba(255,215,0,.25) !important; }
.stCodeBlock pre { background:#0d1f3a !important; }
.stCodeBlock code { color:#64ffda !important; }
div[data-testid="stDataFrameResizable"] { background:#112240 !important; border:1px solid #1e3a5f !important; border-radius:8px !important; }
div[data-testid="stSidebar"] { background:linear-gradient(180deg,#0d1b2a,#112240) !important; border-right:1px solid #1e3a5f !important; }
div[data-testid="stSidebar"] * { color:#e6f1ff !important; }
div[data-testid="stExpander"] { background:#112240 !important; border:1px solid #1e3a5f !important; border-radius:8px !important; }
iframe { border:none !important; }
</style>
""", unsafe_allow_html=True)
