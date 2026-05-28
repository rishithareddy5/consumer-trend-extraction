"""
view/ui.py
Consumer Trend Extraction — Field Intelligence Platform
"""
from __future__ import annotations
import json, os, time
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

API_URL = os.getenv("CTE_API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Consumer Trend Extraction | Field Intelligence",
    page_icon="📊", layout="wide", initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@500;600&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; font-size: 18px !important; }
* { font-size: inherit; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 2.5rem 2rem 2.5rem !important; max-width: 1500px; }

/* BRIGHT WHITE BACKGROUND */
.stApp { background: #F0F4FF !important; }

/* HERO — deep electric blue */
.hero {
    background: linear-gradient(135deg, #1E3A8A 0%, #1D4ED8 50%, #2563EB 100%);
    border-radius: 24px;
    padding: 2.5rem 3rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 20px 60px rgba(37,99,235,0.35);
    position: relative; overflow: hidden;
}
.hero::after {
    content: '';
    position: absolute; top: -100px; right: -100px;
    width: 350px; height: 350px;
    background: radial-gradient(circle, rgba(255,255,255,0.08) 0%, transparent 70%);
    border-radius: 50%;
}
.hero-title {
    color: #FFFFFF !important;
    font-size: 3rem !important;
    font-weight: 900 !important;
    margin: 0 0 0.4rem 0 !important;
    letter-spacing: -0.03em;
    text-shadow: 0 2px 20px rgba(0,0,0,0.2);
}
.hero-sub { color: #BFDBFE !important; font-size: 1.4rem !important; margin: 0 0 1.5rem 0 !important; }
.badge-row { display: flex; gap: 0.6rem; flex-wrap: wrap; }
.badge {
    background: rgba(255,255,255,0.15);
    border: 1.5px solid rgba(255,255,255,0.3);
    color: #FFFFFF;
    padding: 0.35rem 1rem;
    border-radius: 25px;
    font-size: 1rem !important;
    font-weight: 600;
    backdrop-filter: blur(10px);
}
.badge.green { background: rgba(16,185,129,0.3); border-color: #6EE7B7; color: #ECFDF5; }
.badge.yellow { background: rgba(245,158,11,0.3); border-color: #FCD34D; color: #FFFBEB; }

/* MODEL CARDS — white with blue accents */
.model-grid { display: grid; grid-template-columns: repeat(4,1fr); gap: 1rem; margin-bottom: 1.5rem; }
.model-card {
    background: #FFFFFF;
    border: none;
    border-radius: 16px;
    padding: 1.3rem 1.5rem;
    box-shadow: 0 4px 20px rgba(37,99,235,0.12);
    border-top: 4px solid #2563EB;
    transition: transform 0.2s, box-shadow 0.2s;
}
.model-card:hover { transform: translateY(-3px); box-shadow: 0 8px 30px rgba(37,99,235,0.2); }
.mc-label { color: #6B7280; font-size: 0.9rem !important; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.4rem; }
.mc-value { color: #1E3A8A; font-size: 1.5rem !important; font-weight: 900; font-family: 'JetBrains Mono',monospace !important; }
.mc-sub { color: #9CA3AF; font-size: 1rem !important; margin-top: 0.2rem; }

/* SECTION LABELS */
.sec-label {
    color: #1D4ED8;
    font-size: 1rem !important;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin: 1.5rem 0 0.8rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid #DBEAFE;
}

/* FIELD REP CARD */
.rep-card {
    background: linear-gradient(135deg, #EFF6FF, #DBEAFE);
    border: 1.5px solid #BFDBFE;
    border-radius: 14px;
    padding: 1rem 1.2rem;
    margin-bottom: 1rem;
    display: flex; align-items: center; gap: 1rem;
}
.rep-avatar {
    width: 50px; height: 50px;
    background: linear-gradient(135deg, #1D4ED8, #3B82F6);
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.3rem; font-weight: 900; color: white;
    flex-shrink: 0;
    box-shadow: 0 4px 12px rgba(37,99,235,0.3);
}
.rep-name { color: #1E3A8A; font-size: 1.2rem !important; font-weight: 800; }
.rep-meta { color: #6B7280; font-size: 1rem !important; margin-top: 0.1rem; }

/* SCENARIO BUTTONS */
.stButton > button {
    background: #FFFFFF !important;
    border: 2px solid #BFDBFE !important;
    color: #1D4ED8 !important;
    border-radius: 12px !important;
    font-size: 0.9rem !important;
    font-weight: 600 !important;
    transition: all 0.2s !important;
    text-align: left !important;
}
.stButton > button:hover {
    border-color: #2563EB !important;
    background: #EFF6FF !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 15px rgba(37,99,235,0.2) !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #1D4ED8, #2563EB) !important;
    border: none !important;
    color: white !important;
    font-weight: 800 !important;
    font-size: 1.2rem !important;
    border-radius: 14px !important;
    padding: 0.75rem 2rem !important;
    box-shadow: 0 6px 20px rgba(37,99,235,0.45) !important;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 10px 30px rgba(37,99,235,0.55) !important;
}

/* INPUT */
.stTextArea textarea {
    background: #FFFFFF !important;
    border: 2px solid #BFDBFE !important;
    border-radius: 14px !important;
    color: #1E3A8A !important;
    font-size: 1.05rem !important;
    line-height: 1.7 !important;
}
.stTextArea textarea:focus { border-color: #2563EB !important; box-shadow: 0 0 0 4px rgba(37,99,235,0.15) !important; }
.stTextArea textarea::placeholder { color: #9CA3AF !important; }

.stSelectbox > div > div {
    background: #FFFFFF !important;
    border: 2px solid #BFDBFE !important;
    color: #1E3A8A !important;
    border-radius: 12px !important;
    font-size: 1rem !important;
}

/* PRIMARY RESULT CARD */
.result-card {
    background: linear-gradient(135deg, #1E3A8A 0%, #2563EB 100%);
    border-radius: 20px;
    padding: 2rem 2.5rem;
    margin: 1rem 0;
    position: relative; overflow: hidden;
    box-shadow: 0 15px 50px rgba(37,99,235,0.4);
}
.result-card::before {
    content: ''; position: absolute; top:0; left:0; right:0; height:5px;
    background: linear-gradient(to right, #60A5FA, #BFDBFE, #60A5FA);
}
.result-rank { color: #BFDBFE; font-size: 1rem !important; font-weight: 700; text-transform: uppercase; letter-spacing: 0.12em; }
.result-trend { color: #FFFFFF; font-size: 1.4rem !important; font-weight: 900; font-family: 'JetBrains Mono',monospace !important; margin: 0.4rem 0; word-break: break-word; }
.result-conf { color: #60A5FA; font-size: 3rem !important; font-weight: 900; font-family: 'JetBrains Mono',monospace !important; }
.result-conf-lbl { color: #93C5FD; font-size: 1.1rem !important; }

/* OEM ACTION — bright green */
.oem-card {
    background: linear-gradient(135deg, #ECFDF5, #D1FAE5);
    border: 2px solid #6EE7B7;
    border-radius: 16px;
    padding: 1.3rem 1.5rem;
    margin: 1rem 0;
    box-shadow: 0 4px 15px rgba(16,185,129,0.15);
}
.oem-title { color: #065F46; font-size: 1rem !important; font-weight: 800; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.5rem; }
.oem-text { color: #064E3B; font-size: 1.15rem !important; line-height: 1.7; font-weight: 500; }

/* EXPLAIN BOX */
.explain-box {
    background: #EFF6FF;
    border: 1.5px solid #BFDBFE;
    border-left: 5px solid #2563EB;
    border-radius: 0 14px 14px 0;
    padding: 1.2rem 1.5rem;
    margin: 0.8rem 0;
}
.explain-title { color: #1D4ED8; font-size: 1rem !important; font-weight: 800; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.5rem; }
.explain-text { color: #1E3A8A; font-size: 1.15rem !important; line-height: 1.7; }

/* METRICS */
.metrics-row { display: grid; grid-template-columns: repeat(3,1fr); gap: 1rem; margin: 1.2rem 0; }
.metric-box {
    background: #FFFFFF;
    border: none;
    border-radius: 14px;
    padding: 1rem 1.5rem;
    text-align: center;
    box-shadow: 0 4px 15px rgba(37,99,235,0.1);
    border-bottom: 3px solid #2563EB;
}
.metric-val { color: #1D4ED8; font-size: 2.2rem !important; font-weight: 900; font-family: 'JetBrains Mono',monospace !important; }
.metric-lbl { color: #6B7280; font-size: 0.95rem !important; text-transform: uppercase; letter-spacing: 0.08em; margin-top: 0.2rem; }

/* SIDEBAR — white */
section[data-testid="stSidebar"] {
    background: #FFFFFF !important;
    border-right: 2px solid #DBEAFE !important;
    box-shadow: 4px 0 20px rgba(37,99,235,0.08) !important;
}
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stCaption { color: #374151 !important; font-size: 1.05rem !important; }

/* TABS */
.stTabs [data-baseweb="tab-list"] {
    background: #FFFFFF;
    border-radius: 14px;
    padding: 5px;
    border: 2px solid #DBEAFE;
    gap: 4px;
    box-shadow: 0 2px 10px rgba(37,99,235,0.08);
}
.stTabs [data-baseweb="tab"] { color: #6B7280 !important; font-weight: 700 !important; font-size: 1.1rem !important; border-radius: 10px !important; padding: 0.5rem 1.8rem !important; }
.stTabs [aria-selected="true"] { background: linear-gradient(135deg, #1D4ED8, #2563EB) !important; color: #FFFFFF !important; box-shadow: 0 4px 12px rgba(37,99,235,0.3) !important; }

/* HISTORY */
.hist-item {
    background: #EFF6FF;
    border: 1.5px solid #BFDBFE;
    border-radius: 10px;
    padding: 0.7rem 1rem;
    margin-bottom: 0.5rem;
}
.hist-trend { color: #1D4ED8; font-family: 'JetBrains Mono',monospace !important; font-size: 1rem !important; font-weight: 700; }
.hist-preview { color: #9CA3AF; font-size: 0.92rem !important; margin-top: 0.2rem; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }

/* PROGRESS */
.stProgress > div > div > div > div { background: linear-gradient(to right, #1D4ED8, #60A5FA) !important; border-radius: 4px !important; }
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-thumb { background: #BFDBFE; border-radius: 3px; }
.streamlit-expanderHeader { background: #EFF6FF !important; border: 1.5px solid #BFDBFE !important; border-radius: 10px !important; color: #1D4ED8 !important; font-size: 0.95rem !important; }
</style>
""", unsafe_allow_html=True)

# ── SESSION STATE ──────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []
if "last_result" not in st.session_state:
    st.session_state.last_result = None

# ── CONSTANTS ──────────────────────────────────────────────────────────
TREND_EXPLANATIONS = {
    "rising_spicy_flavor_preference": "Strong demand for high-heat variants among teenagers and youth near educational institutions. Mild variants are losing shelf movement rapidly.",
    "youth_driven_consumption": "Evening and weekend sales disproportionately driven by college-age consumers. Their preferences are rapidly reshaping which SKUs move.",
    "fusion_flavor_adoption": "Consumers requesting hybrid flavors — schezwan namkeen, cheesy masala, indo-western combos. Competitor products are driving awareness.",
    "western_snack_influence": "Digital media exposure creating demand for dip formats, cheesy variants, and globally-inspired styles among kids and teens.",
    "health_conscious_snacking": "Consumers actively reading nutritional labels. Calorie count and ingredient lists are now primary purchase decision factors.",
    "premium_packaging_demand": "Gift-ready, aesthetically premium packaging requested especially during festivals. Plain pouches rejected for gifting occasions.",
    "regional_flavor_revival": "Demand for hyper-local, traditional flavor profiles resurging. Consumers cite national brands taste identical everywhere.",
    "convenience_format_preference": "Single-serve, on-the-go formats preferred by urban commuters who cannot consume large packs in transit.",
    "festive_gifting_trend": "Festival periods see 3-5x volume spikes in gift pack formats. Regular inventory ignored during these windows.",
    "online_impulse_buying": "Consumers discovering products on social media and quick-commerce apps before visiting physical stores.",
    "sugar_free_demand": "Diabetic and health-aware consumers actively requesting sugar-free snack variants. Retailers report daily queries going unmet.",
    "protein_snack_trend": "Gym culture creating new demand for protein-forward snacks. Traditional chips rejected in favor of high-protein alternatives.",
    "small_pack_affordability_preference": "Rs.5-Rs.10 price points dominate volume in price-sensitive markets. Premium SKUs see minimal offtake.",
    "plant_based_adoption": "Vegan and plant-based queries rising even among non-vegans, driven by health perception. A new and growing segment.",
    "tangy_sour_flavor_rise": "Raw mango, imli, and citrus-forward flavors consistently out of stock. Demand outpaces supply in most markets surveyed.",
}

OEM_ACTIONS = {
    "rising_spicy_flavor_preference": "🌶️ Launch ghost pepper / extra-hot variants in Tier-2 cities. Reformulate existing SKUs to add heat levels. Target college-area distributors.",
    "youth_driven_consumption": "📱 Increase Instagram/Reels presence. Launch limited-edition SKUs with youth-centric branding. Evening in-store promotions near colleges.",
    "fusion_flavor_adoption": "🧪 Fast-track schezwan-masala and cheesy variants in NPD pipeline. Counter competitor movement within 60 days.",
    "western_snack_influence": "🧀 Introduce dip-compatible formats and cheese-flavored range. Target kids segment with cartoon tie-ins.",
    "health_conscious_snacking": "💚 Revamp packaging to prominently display calorie count. Launch Better-for-You product line with clean labels.",
    "premium_packaging_demand": "🎁 Develop festival gift-pack SKUs. Launch tiered gift boxes at Rs.99/199/299. Position 6 weeks before major festivals.",
    "regional_flavor_revival": "🏘️ Develop region-specific variants (mango pickle South, mustard East). Partner with local flavor houses.",
    "convenience_format_preference": "🚀 Expand single-serve Rs.5-Rs.10 range. Focus distribution on transit hubs, bus stands, metro stations.",
    "festive_gifting_trend": "🪔 Pre-position festive gift inventory 8 weeks in advance. Create premium gifting range Rs.99-299.",
    "online_impulse_buying": "📦 List on Swiggy Instamart/Zepto/Blinkit. Run social discovery campaigns. Optimize quick-commerce shelf.",
    "sugar_free_demand": "🩺 Develop sugar-free namkeen variants. Distribute through medical stores. Partner with diabetic associations.",
    "protein_snack_trend": "💪 Launch high-protein roasted snack range. Distribute through gyms. Highlight protein content on pack.",
    "small_pack_affordability_preference": "💰 Ensure Rs.5 and Rs.10 SKU availability at all outlets. Prioritize volume over margin in price-sensitive zones.",
    "plant_based_adoption": "🌱 Introduce plant-based certified variants. Add vegan labeling to eligible products. Target health food stores.",
    "tangy_sour_flavor_rise": "🍋 Increase raw mango and tamarind variant production. Review supply chain for stockout prevention. Launch seasonal campaigns.",
}

LABEL_CATEGORIES = {
    "Flavor & Taste": ["rising_spicy_flavor_preference","fusion_flavor_adoption","regional_flavor_revival","tangy_sour_flavor_rise"],
    "Health & Wellness": ["health_conscious_snacking","sugar_free_demand","protein_snack_trend","plant_based_adoption"],
    "Consumer Behavior": ["youth_driven_consumption","western_snack_influence","convenience_format_preference","online_impulse_buying"],
    "Market & Commerce": ["premium_packaging_demand","festive_gifting_trend","small_pack_affordability_preference"],
}
CAT_COLORS = {"Flavor & Taste":"#F59E0B","Health & Wellness":"#10B981","Consumer Behavior":"#8B5CF6","Market & Commerce":"#EC4899"}

FIELD_REPS = [
    {"name":"Priya Sharma","city":"Hyderabad","region":"South India","stores":12,"avatar":"P"},
    {"name":"Rahul Nair","city":"Mumbai","region":"West India","stores":18,"avatar":"R"},
    {"name":"Deepa Iyer","city":"Chennai","region":"South India","stores":9,"avatar":"D"},
    {"name":"Arjun Patel","city":"Ahmedabad","region":"West India","stores":15,"avatar":"A"},
    {"name":"Sunita Rao","city":"Bengaluru","region":"South India","stores":11,"avatar":"S"},
]

DEMO_SCENARIOS = [
    {"tag":"🌶️ Flavor","city":"Bhopal · Teenagers","text":"Retailer says mild variants not moving at all. Customers asking for extra spicy only."},
    {"tag":"🩺 Health","city":"Bhubaneswar · Adults","text":"Diabetic customers asking for sugar-free namkeen regularly. Nothing to offer them now."},
    {"tag":"🎁 Gifting","city":"Kolkata · Premium","text":"Festival week retailer sold 3x normal volume. All gift packs. Regular stock sat untouched."},
    {"tag":"💰 Price","city":"Bangalore · College","text":"Only the cheapest five rupee packs sell here. Customers cannot afford anything bigger."},
    {"tag":"🧀 Western","city":"Chandigarh · Kids","text":"Kids asking for cheesy nacho dips like the imported western brands they saw in ads."},
    {"tag":"💪 Protein","city":"Bhopal · Urban Youth","text":"Gym nearby sending customers — all asking for high-protein snacks. No chips, only protein."},
]

MULTI_CITY = [
    {"city":"Hyderabad","feedback":"College students near Osmania University asking for ghost pepper chips. Regular spice not enough."},
    {"city":"Mumbai","feedback":"Commuters at Dadar station want single-serve packs. Can't eat large pack while standing in train."},
    {"city":"Chennai","feedback":"Diabetic customers asking for sugar-free snacks daily. 5-6 queries every day going unanswered."},
    {"city":"Delhi","feedback":"Customers requesting gift-ready boxes for Diwali. Plain pouches rejected. Premium packaging only."},
    {"city":"Bengaluru","feedback":"Gym crowd asking for protein snacks only. No chips, high-protein alternatives only."},
]

def call_predict(api_url, feedback):
    try:
        r = requests.post(f"{api_url}/predict", json={"retailer_feedback":feedback.strip()}, timeout=120)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None

def get_category(trend):
    for cat, labs in LABEL_CATEGORIES.items():
        if trend in labs: return cat
    return "Other"

def conf_color_bright(conf):
    if conf >= 0.6: return "#059669"
    if conf >= 0.3: return "#2563EB"
    if conf >= 0.1: return "#D97706"
    return "#9CA3AF"

def make_bar_chart(result):
    trends = [result["primary_trend"], result["secondary_trend"], result["tertiary_trend"]]
    confs = [result["primary_confidence"]*100, result["secondary_confidence"]*100, result["tertiary_confidence"]*100]
    colors = [conf_color_bright(c/100) for c in confs]
    short = [t.replace("_"," ").title() for t in trends]
    fig = go.Figure(go.Bar(
        x=confs, y=short, orientation='h',
        marker=dict(color=colors, line=dict(color='rgba(255,255,255,0.5)',width=1)),
        text=[f"  {c:.1f}%" for c in confs],
        textposition='outside',
        textfont=dict(color='#1E3A8A', size=18, family='JetBrains Mono'),
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(239,246,255,0.8)',
        font=dict(color='#374151', family='Inter', size=16),
        xaxis=dict(showgrid=True, gridcolor='rgba(37,99,235,0.15)',
                   zeroline=False, range=[0, max(confs)*1.5],
                   tickfont=dict(size=15, color='#6B7280'),
                   title=dict(text='Confidence Score (%)', font=dict(size=14, color='#9CA3AF'))),
        yaxis=dict(showgrid=False, tickfont=dict(size=16, color='#1E3A8A', family='Inter'), autorange='reversed'),
        height=280, margin=dict(l=10, r=90, t=20, b=50), bargap=0.4,
    )
    return fig

def make_gauge(conf):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=conf*100,
        number=dict(suffix="%", font=dict(size=40, color="#1D4ED8", family="JetBrains Mono")),
        gauge=dict(
            axis=dict(range=[0,100], tickfont=dict(color='#6B7280',size=12), nticks=6),
            bar=dict(color="#2563EB", thickness=0.7),
            bgcolor="rgba(239,246,255,0.8)",
            borderwidth=2, bordercolor="#BFDBFE",
            steps=[
                dict(range=[0,30], color="rgba(156,163,175,0.15)"),
                dict(range=[30,65], color="rgba(37,99,235,0.1)"),
                dict(range=[65,100], color="rgba(5,150,105,0.15)"),
            ],
        ),
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter', color='#374151'),
        height=200, margin=dict(l=20, r=20, t=20, b=10),
    )
    return fig

def make_donut(cat_counts):
    labels = list(cat_counts.keys())
    values = list(cat_counts.values())
    colors = [CAT_COLORS.get(l,"#2563EB") for l in labels]
    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.55,
        marker=dict(colors=colors, line=dict(color='white', width=3)),
        textinfo='label+percent',
        textfont=dict(size=13, color='#1E3A8A', family='Inter'),
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#374151', family='Inter'),
        height=280, margin=dict(l=10, r=10, t=20, b=10),
        legend=dict(font=dict(size=12, color='#374151'), bgcolor='rgba(0,0,0,0)'),
        annotations=[dict(text='Trends', x=0.5, y=0.5, font_size=14, showarrow=False, font_color='#6B7280')],
    )
    return fig

def make_city_chart(city_results):
    cities = [r["city"] for r in city_results]
    confs = [round(r["primary_confidence"]*100,1) for r in city_results]
    trends = [r["primary_trend"].replace("_"," ").title() for r in city_results]
    cats = [get_category(r["primary_trend"]) for r in city_results]
    colors = [CAT_COLORS.get(c,"#2563EB") for c in cats]
    fig = go.Figure()
    for city, conf, trend, color in zip(cities, confs, trends, colors):
        fig.add_trace(go.Bar(
            name=city, x=[city], y=[conf],
            marker_color=color,
            text=f"{trend}<br>{conf}%",
            textposition='inside',
            textfont=dict(size=12, color='white', family='Inter'),
            width=0.5,
        ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(239,246,255,0.8)',
        font=dict(color='#374151', family='Inter', size=13),
        xaxis=dict(showgrid=False, tickfont=dict(size=14, color='#1E3A8A')),
        yaxis=dict(showgrid=True, gridcolor='rgba(37,99,235,0.15)',
                   title='Confidence (%)', tickfont=dict(size=12, color='#6B7280'), range=[0,100]),
        height=300, margin=dict(l=10,r=10,t=20,b=40), showlegend=False, bargap=0.3,
    )
    return fig

# ── SIDEBAR ────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:1rem 0 0.3rem;">
        <div style="color:#2563EB;font-size:0.72rem;font-weight:800;text-transform:uppercase;letter-spacing:0.12em;">Field Intelligence Platform</div>
        <div style="color:#1E3A8A;font-size:1.3rem;font-weight:900;margin-top:0.3rem;">CTE System</div>
        <div style="color:#9CA3AF;font-size:0.88rem;margin-top:0.1rem;">Retailer Trend Detector</div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    st.markdown('<div style="color:#2563EB;font-size:0.78rem;font-weight:800;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.5rem;">Field Representative</div>', unsafe_allow_html=True)
    rep_names = [f"{r['name']} · {r['city']}" for r in FIELD_REPS]
    selected = st.selectbox("Rep", rep_names, label_visibility="collapsed")
    rep = FIELD_REPS[rep_names.index(selected)]
    st.markdown(f'''<div style="background:linear-gradient(135deg,#EFF6FF,#DBEAFE);border:1.5px solid #BFDBFE;border-radius:10px;padding:0.6rem 1rem;margin-top:0.3rem;display:flex;align-items:center;gap:0.8rem;">
        <div style="width:36px;height:36px;background:linear-gradient(135deg,#1D4ED8,#3B82F6);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:1rem;font-weight:900;color:white;flex-shrink:0;">{rep["avatar"]}</div>
        <div>
            <div style="color:#1E3A8A;font-size:0.95rem;font-weight:800;">{rep["name"]}</div>
            <div style="color:#6B7280;font-size:0.78rem;">{rep["city"]} · {rep["stores"]} stores</div>
        </div>
    </div>''', unsafe_allow_html=True)


    api_url = API_URL

    min_conf = 0

    st.divider()
    st.markdown('<div style="color:#2563EB;font-size:0.78rem;font-weight:800;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.5rem;">Category Filter</div>', unsafe_allow_html=True)
    selected_cats = []
    for cat, color in CAT_COLORS.items():
        if st.checkbox(f"**{cat}**", value=True, key=f"cat_{cat}"):
            selected_cats.append(cat)
    allowed_labels = []
    for cat in selected_cats:
        allowed_labels.extend(LABEL_CATEGORIES[cat])

    st.divider()
    st.markdown('<div style="color:#2563EB;font-size:0.78rem;font-weight:800;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.5rem;">15 Trend Labels</div>', unsafe_allow_html=True)
    try:
        labs = requests.get(f"{api_url}/labels", timeout=3).json()["labels"]
        for cat, cat_labs in LABEL_CATEGORIES.items():
            color = CAT_COLORS.get(cat,"#2563EB")
            st.markdown(f'''<div style="margin-bottom:0.5rem;">
                <div style="color:{color};font-size:0.75rem;font-weight:800;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.3rem;">{cat}</div>
                {"".join([f'<span style="display:inline-block;background:{color}18;border:1px solid {color}44;color:{color};padding:2px 8px;border-radius:12px;font-size:0.75rem;font-weight:600;margin:2px;font-family:monospace;">{l.replace("_"," ")}</span>' for l in cat_labs])}
            </div>''', unsafe_allow_html=True)
    except Exception:
        for cat, cat_labs in LABEL_CATEGORIES.items():
            color = CAT_COLORS.get(cat,"#2563EB")
            st.markdown(f'''<div style="margin-bottom:0.5rem;">
                <div style="color:{color};font-size:0.75rem;font-weight:800;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.3rem;">{cat}</div>
                {"".join([f'<span style="display:inline-block;background:{color}18;border:1px solid {color}44;color:{color};padding:2px 8px;border-radius:12px;font-size:0.75rem;font-weight:600;margin:2px;font-family:monospace;">{l.replace("_"," ")}</span>' for l in cat_labs])}
            </div>''', unsafe_allow_html=True)

    if st.session_state.history:
        st.divider()
        st.markdown('<div style="color:#2563EB;font-size:0.78rem;font-weight:800;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.5rem;">Session History</div>', unsafe_allow_html=True)
        for i, item in enumerate(reversed(st.session_state.history[-5:])):
            st.markdown(f"""
            <div class="hist-item">
                <div class="hist-trend">#{len(st.session_state.history)-i} {item['primary_trend']}</div>
                <div class="hist-preview">{item['feedback'][:50]}...</div>
            </div>
            """, unsafe_allow_html=True)
        if st.button("Clear History", use_container_width=True):
            st.session_state.history = []
            st.rerun()

# ── HERO ───────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="hero">
    <div class="hero-title">Consumer Trend Extraction</div>
    <div class="hero-sub">Detect emerging FMCG consumer trends from retailer field observations · {rep['name']} reporting from {rep['city']}</div>
    <div class="badge-row">
        <span class="badge">Gemma 2B IT</span>
        <span class="badge">QLoRA Fine-tuned</span>
        <span class="badge">LoRA Adapter</span>
        <span class="badge">500 Retailer Notes</span>
        <span class="badge">FastAPI Backend</span>
        <span class="badge green">15 Trend Labels</span>
        <span class="badge yellow">80.95% Accuracy</span>
    </div>
</div>
""", unsafe_allow_html=True)



tab1, tab2, tab3 = st.tabs(["  🔍  Single Prediction  ","  🗺️  Multi-City Intelligence  ","  📂  Batch Upload  "])

# ════════════════════════════════════════════════════════════════════
# TAB 1
# ════════════════════════════════════════════════════════════════════
with tab1:
    col_left, col_right = st.columns([1.1, 0.9], gap="large")
    with col_left:
        st.markdown('<div class="sec-label">📝 Enter Retailer Feedback</div>', unsafe_allow_html=True)
        
        default_fb = st.session_state.get("selected_scenario", st.session_state.get("last_feedback",""))
        feedback = st.text_area("Feedback", value=default_fb, height=180,
            placeholder="e.g. Customers asking for sugar-free biscuits. Owner says 5-6 queries daily going unmet.",
            label_visibility="collapsed")
        if feedback:
            st.session_state["last_feedback"] = feedback
            st.session_state["last_feedback"] = feedback

        char_count = len(feedback.strip())
        st.markdown(f'<div style="color:#9CA3AF;font-size:1rem;text-align:right;margin-top:-0.5rem;">{char_count} / 2000</div>', unsafe_allow_html=True)

        c1, c2 = st.columns([2,1])
        with c1:
            extract_btn = st.button("⚡  Extract Trends", type="primary", use_container_width=True)
        with c2:
            if st.button("Clear", use_container_width=True):
                st.session_state["last_feedback"] = ""
                st.session_state["selected_scenario"] = ""
                st.session_state.last_result = None
                st.rerun()

        st.markdown('<div class="sec-label" style="margin-top:1.5rem;">💡 Try a Demo Example</div>', unsafe_allow_html=True)
        st.markdown('<div style="color:#9CA3AF;font-size:0.95rem;margin-bottom:0.8rem;">Click to auto-fill with real field data</div>', unsafe_allow_html=True)
        
        selected_scenario = None
        cols = st.columns(2)
        for i, sc in enumerate(DEMO_SCENARIOS):
            with cols[i % 2]:
                if st.button(f"{sc['tag']} {sc['city']}", key=f"sc_{i}", use_container_width=True):
                    st.session_state["selected_scenario"] = sc["text"]
                    st.rerun()

        st.markdown("""
        <div style="margin-top:1.8rem;background:#FFFFFF;border:1px solid #E2E8F0;border-left:4px solid #2563EB;border-radius:14px;padding:1.2rem 1.4rem;box-shadow:0 1px 3px rgba(0,0,0,0.04);">
            <div style="color:#1D4ED8;font-size:1rem;font-weight:800;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.6rem;">How It Works</div>
            <div style="color:#334155;font-size:1.02rem;line-height:1.65;">Gemma 2B IT, fine-tuned with <b>QLoRA</b> on 500 retailer notes across 15 consumer-trend labels. Each prediction is the model's own ranked confidence over the label set, computed by greedy decoding, so the same feedback always yields the same result.</div>
        </div>
        """, unsafe_allow_html=True)


    with col_right:
        st.markdown('<div class="sec-label">📊 Prediction Results</div>', unsafe_allow_html=True)
        if extract_btn:
            if char_count < 3:
                st.warning("Please enter at least 3 characters.")
            else:
                with st.spinner(f"Running Gemma 2B + LoRA for {rep['name']}..."):
                    t0 = time.time()
                    result = call_predict(api_url, feedback)
                    latency_ms = (time.time() - t0) * 1000
                if result is None:
                    st.error("Cannot reach API. Make sure FastAPI is running on port 8000.")
                else:
                    st.session_state.last_result = {"result": result, "feedback": feedback, "latency_ms": latency_ms}
                    st.session_state.history.append({"feedback": feedback, "primary_trend": result["primary_trend"], "primary_confidence": result["primary_confidence"], "result": result})

        if st.session_state.last_result:
            result = st.session_state.last_result["result"]
            latency_ms = st.session_state.last_result["latency_ms"]
            st.markdown(f"""
            <div class="metrics-row">
                <div class="metric-box"><div class="metric-val">{latency_ms:.0f}ms</div><div class="metric-lbl">Inference</div></div>
                <div class="metric-box"><div class="metric-val">{result['primary_confidence']*100:.1f}%</div><div class="metric-lbl">Confidence</div></div>
                <div class="metric-box"><div class="metric-val">3</div><div class="metric-lbl">Trends</div></div>
            </div>
            """, unsafe_allow_html=True)

            primary = result["primary_trend"]
            primary_conf = result["primary_confidence"]
            cat = get_category(primary)
            cat_color = CAT_COLORS.get(cat, "#2563EB")

            st.markdown(f"""
            <div class="result-card">
                <div class="result-rank">🥇 Primary Trend · {rep['city']}</div>
                <div class="result-trend">{primary}</div>
                <div class="result-conf">{primary_conf*100:.1f}%</div>
                <div class="result-conf-lbl">confidence score</div>
                <div style="margin-top:0.8rem;">
                    <span style="background:rgba(255,255,255,0.15);border:1.5px solid rgba(255,255,255,0.3);
                    color:#FFFFFF;padding:0.3rem 0.9rem;border-radius:20px;font-size:0.85rem;font-weight:700;">
                    📂 {cat}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            _exp = TREND_EXPLANATIONS.get(primary, "") or "This trend was inferred from the retailer feedback signals."
            _why_title = primary.replace("_", " ").title()
            st.markdown(f"""
            <div class="explain-box" style="margin-top:1rem;margin-bottom:1rem;">
                <div class="explain-title">💡 Why {_why_title}?</div>
                <div class="explain-text">{_exp}</div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown('<div style="color:#6B7280;font-size:0.85rem;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.3rem;">Confidence Comparison</div>', unsafe_allow_html=True)
            st.plotly_chart(make_bar_chart(result), use_container_width=True, config={"displayModeBar":False})

            oem = OEM_ACTIONS.get(primary, "Review trend signal and initiate NPD discussion.")
            st.markdown(f"""
            <div class="oem-card">
                <div class="oem-title">💡 OEM Action Recommendation</div>
                <div class="oem-text">{oem}</div>
            </div>
            """, unsafe_allow_html=True)



            with st.expander("📋  Raw JSON + Download"):
                payload = {k: result[k] for k in result if k != "raw_generation"}
                st.code(json.dumps(payload, indent=2), language="json")
                st.download_button("⬇  Download JSON", data=json.dumps(payload, indent=2),
                    file_name=f"cte_{primary}.json", mime="application/json")
        else:
            st.markdown("""
            <div style="text-align:center;padding:4rem 1rem;">
                <div style="font-size:3.5rem;margin-bottom:1rem;">📊</div>
                <div style="font-size:1.3rem;font-weight:800;color:#6B7280;">Click a scenario or enter retailer feedback</div>
                <div style="font-size:1.05rem;margin-top:0.5rem;color:#9CA3AF;">Trends + charts + OEM recommendations will appear here</div>
            </div>
            """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════
# TAB 2 — MULTI-CITY
# ════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="sec-label">🗺️ Multi-City Trend Intelligence</div>', unsafe_allow_html=True)
    st.markdown('<div style="color:#374151;font-size:1.1rem;margin-bottom:1.5rem;">Analyse retailer feedback from multiple cities simultaneously to detect regional trend patterns</div>', unsafe_allow_html=True)

    col_a, col_b = st.columns([1, 1], gap="large")
    with col_a:
        st.markdown('<div style="color:#2563EB;font-size:0.82rem;font-weight:800;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.8rem;">City Feedback Inputs</div>', unsafe_allow_html=True)
        city_inputs = []
        for i, sc in enumerate(MULTI_CITY):
            with st.expander(f"📍 {sc['city']}", expanded=(i==0)):
                fb = st.text_area(f"Feedback_{i}", value=sc["feedback"], height=80, key=f"city_{i}", label_visibility="collapsed")
                city_inputs.append({"city": sc["city"], "feedback": fb})
        run_multi = st.button("⚡  Analyse All Cities", type="primary", use_container_width=True)

    with col_b:
        st.markdown('<div style="color:#2563EB;font-size:0.82rem;font-weight:800;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.8rem;">Regional Intelligence</div>', unsafe_allow_html=True)
        if run_multi:
            city_results = []
            prog = st.progress(0)
            for i, inp in enumerate(city_inputs):
                if inp["feedback"].strip():
                    prog.progress((i+1)/len(city_inputs), text=f"Analysing {inp['city']}...")
                    res = call_predict(api_url, inp["feedback"])
                    if res:
                        city_results.append({"city": inp["city"], "primary_trend": res["primary_trend"],
                            "primary_confidence": res["primary_confidence"], "secondary_trend": res["secondary_trend"],
                            "category": get_category(res["primary_trend"])})
            prog.empty()
            if city_results:
                st.session_state["city_results"] = city_results

        if "city_results" in st.session_state and st.session_state["city_results"]:
            cr = st.session_state["city_results"]
            st.markdown('<div style="color:#6B7280;font-size:0.82rem;font-weight:700;text-transform:uppercase;margin-bottom:0.3rem;">Trend Signal by City</div>', unsafe_allow_html=True)
            st.plotly_chart(make_city_chart(cr), use_container_width=True, config={"displayModeBar":False})

            cat_counts = {}
            for r in cr:
                cat_counts[r["category"]] = cat_counts.get(r["category"], 0) + 1
            st.markdown('<div style="color:#6B7280;font-size:0.82rem;font-weight:700;text-transform:uppercase;margin-bottom:0.3rem;">Category Distribution</div>', unsafe_allow_html=True)
            st.plotly_chart(make_donut(cat_counts), use_container_width=True, config={"displayModeBar":False})

            df_city = pd.DataFrame(cr)[["city","primary_trend","category"]]
            df_city.columns = ["City","Primary Trend","Category"]
            st.dataframe(df_city, use_container_width=True, hide_index=True)
        else:
            st.markdown("""
            <div style="text-align:center;padding:3rem 1rem;">
                <div style="font-size:3rem;margin-bottom:1rem;">🗺️</div>
                <div style="font-size:1.05rem;font-weight:700;color:#9CA3AF;">Click Analyse All Cities</div>
                <div style="font-size:0.9rem;margin-top:0.5rem;color:#CBD5E1;">City charts and category distribution will appear here</div>
            </div>
            """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════
# TAB 3 — BATCH
# ════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="sec-label">📂 Batch CSV Processing</div>', unsafe_allow_html=True)
    col_x, col_y = st.columns([1,1], gap="large")
    with col_x:
        st.markdown("""
        <div class="explain-box">
            <div class="explain-title">CSV Format</div>
            <div class="explain-text">
                Upload a CSV with a <code style="color:#1D4ED8;background:#DBEAFE;padding:2px 6px;border-radius:4px;">retailer_feedback</code> column.
                Results are appended as new columns.<br><br>
                <strong>Optional:</strong> city, store_id, visit_date, consumer_demographic
            </div>
        </div>
        """, unsafe_allow_html=True)
        sample = "retailer_feedback,city,store_id\n\"Mild variants not moving. Customers asking for extra spicy.\",Bhopal,BHO001\n\"Diabetic customers asking for sugar-free namkeen.\",Bhubaneswar,BHU042\n\"Rs.5 and Rs.10 packs selling highest volume.\",Bangalore,BLR019\n\"College students driving evening sales completely.\",Vizag,VIZ007\n\"Festival week sold 3x. All gift packs.\",Kolkata,KOL033\n"
        st.download_button("⬇  Download Sample CSV", data=sample, file_name="sample_batch.csv", mime="text/csv", use_container_width=True)
    with col_y:
        uploaded = st.file_uploader("Upload CSV", type=["csv"], label_visibility="collapsed")
        if uploaded:
            try: df = pd.read_csv(uploaded)
            except Exception as e:
                st.error(f"Could not read: {e}"); df = None
            if df is not None:
                if "retailer_feedback" not in df.columns:
                    st.error("CSV must have a `retailer_feedback` column.")
                else:
                    st.success(f"✓ Loaded {len(df)} rows")
                    st.dataframe(df.head(3), use_container_width=True)
                    if st.button("⚡  Run Batch", type="primary", use_container_width=True):
                        results_list = []
                        prog = st.progress(0)
                        status = st.empty()
                        for i, row in df.iterrows():
                            text = str(row["retailer_feedback"])
                            status.markdown(f'<div style="color:#2563EB;font-size:0.95rem;">Processing {i+1}/{len(df)}: {text[:45]}...</div>', unsafe_allow_html=True)
                            prog.progress((i+1)/len(df))
                            res = call_predict(api_url, text)
                            if res:
                                results_list.append({"primary_trend": res["primary_trend"], "primary_conf_%": round(res["primary_confidence"]*100,1),
                                    "secondary_trend": res["secondary_trend"], "secondary_conf_%": round(res["secondary_confidence"]*100,1),
                                    "category": get_category(res["primary_trend"])})
                            else:
                                results_list.append({"primary_trend":"ERROR","primary_conf_%":0,"secondary_trend":"","secondary_conf_%":0,"category":"Error"})
                        status.empty(); prog.empty()
                        rdf = pd.DataFrame(results_list)
                        final = pd.concat([df.reset_index(drop=True), rdf], axis=1)
                        st.success(f"✅ {len(final)} predictions complete")
                        st.dataframe(final, use_container_width=True)
                        cat_counts = final["category"].value_counts().to_dict()
                        st.plotly_chart(make_donut(cat_counts), use_container_width=True, config={"displayModeBar":False})
                        st.download_button("⬇  Download Results", data=final.to_csv(index=False),
                            file_name="cte_batch_results.csv", mime="text/csv", use_container_width=True)

st.markdown("""
<div style="margin-top:3rem;padding:1.5rem 0;border-top:2px solid #BFDBFE;
     display:flex;justify-content:space-between;flex-wrap:wrap;gap:0.5rem;">
    <div style="color:#374151;font-size:0.95rem;font-weight:500;">Consumer Trend Extraction · Gemma 2B IT + QLoRA · Field Intelligence Platform</div>
    <div style="color:#374151;font-size:0.95rem;font-weight:500;">Deterministic greedy decoding · 15 trend labels · FastAPI backend</div>
</div>
""", unsafe_allow_html=True)
