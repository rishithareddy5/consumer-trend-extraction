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
CAT_COLORS = {"Flavor & Taste":"#EAB308","Health & Wellness":"#9333EA","Consumer Behavior":"#EF4444","Market & Commerce":"#EC4899"}
CAT_COLORS_CHART = dict(CAT_COLORS); CAT_COLORS_CHART["Other"]="#94A3B8"

# Compute FIELD_REPS dynamically from the actual dataset
def _build_field_reps():
    try:
        _df = pd.read_csv("data/dataset.csv", keep_default_na=False)
        _reps = []
        for rep_name in sorted(_df['salesperson_name'].unique()):
            _sub = _df[_df['salesperson_name'] == rep_name]
            _city = _sub['city'].iloc[0]
            _n_retailers = _sub['retailer_id'].nunique()
            _n_visits = len(_sub)
            _reps.append({
                "name": rep_name,
                "city": _city,
                "region": "",
                "stores": _n_retailers,
                "visits": _n_visits,
                "avatar": rep_name[0].upper(),
            })
        return _reps
    except Exception:
        return [{"name":"Default Rep","city":"Bangalore","region":"","stores":1,"visits":0,"avatar":"D"}]

FIELD_REPS = _build_field_reps()

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
            <div style="color:#6B7280;font-size:0.78rem;">{rep["city"]} · {rep["stores"]} retailer · {rep["visits"]} visits</div>
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
    st.markdown('<div style="color:#2563EB;font-size:0.78rem;font-weight:800;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.5rem;">16 Trend Labels</div>', unsafe_allow_html=True)
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
        <span class="badge">515 Retailer Notes</span>
        <span class="badge">FastAPI Backend</span>
        <span class="badge">16 Trend Labels</span>
        <span class="badge">78.9% Accuracy · 16 Trends</span>
    </div>
</div>
""", unsafe_allow_html=True)



tab_chat, tab3 = st.tabs(["  💬  Smart Chat  ","  📂  Batch Upload  "])

# ════════════════════════════════════════════════════════════════════
# TAB 1
# ════════════════════════════════════════════════════════════════════
if False:  # Single Prediction tab hidden — replaced by Smart Chat
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
            is_oos = result.get("out_of_scope", False) or primary == "OUT_OF_SCOPE"
            cat = get_category(primary) if not is_oos else "Out of Scope"
            cat_color = CAT_COLORS.get(cat, "#DC2626" if is_oos else "#2563EB")

            if is_oos:
                st.markdown(f"""
                <div class="result-card" style="background:linear-gradient(135deg,#DC2626 0%,#991B1B 100%);">
                    <div class="result-rank">⚠️ OUT OF SCOPE · {rep['city']}</div>
                    <div class="result-trend" style="font-size:1.4rem;">Note does not fit trained categories</div>
                    <div class="result-conf">{primary_conf*100:.1f}%</div>
                    <div class="result-conf-lbl">top match confidence (below 30% threshold)</div>
                    <div style="margin-top:0.8rem;">
                        <span style="background:rgba(255,255,255,0.2);border:1.5px solid rgba(255,255,255,0.4);
                        color:#FFFFFF;padding:0.3rem 0.9rem;border-radius:20px;font-size:0.85rem;font-weight:700;">
                        ⚠️ Model not trained on this kind of feedback</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
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
if False:  # Multi-City tab hidden — code preserved for later
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

with tab_chat:
    st.markdown('<div class="sec-label">💬 Smart Chat — Ask Anything</div>', unsafe_allow_html=True)
    st.markdown('<div style="color:#6B7280;font-size:0.9rem;margin-bottom:1rem;">Choose a mode above, then type below — Classify a single note, or ask an Analytics question about the data.</div>', unsafe_allow_html=True)

    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Trend label list for intent detection
    TREND_KEYWORDS = [
        'spicy', 'fusion', 'regional', 'tangy', 'sour', 'youth', 'sugar_free', 'sugar-free',
        'protein', 'plant_based', 'plant-based', 'health', 'convenience', 'online', 'impulse',
        'western', 'festive', 'gifting', 'premium', 'packaging', 'small_pack', 'affordability',
        'no_trend', 'rising_spicy', 'youth_driven', 'youth_driven_consumption'
    ]
    ANALYTICS_VERBS = [
        'show me', 'show', 'analyze', 'analysis', 'compare', 'comparison', 'how many',
        'what trend', 'which city', 'which season', 'breakdown', 'distribution', 'chart',
        'graph', 'count', 'list', 'rank', 'top ', 'best', 'worst', 'across', 'by city',
        'by season', 'by demographic', 'what sells', 'what sell', 'who buys', 'where is',
        'when is', 'top trends', 'top trend', 'trends in', 'trend in', 'give me',
        'tell me', 'what is selling', 'what about', 'most common', 'most popular'
    ]

    def _detect_intent(q: str) -> str:
        import re as _re
        ql = q.lower().strip()
        # Analytics verbs always route to analytics — use word-boundary match to avoid 'top' matching 'laptop'
        for _v in ANALYTICS_VERBS:
            _v_clean = _v.strip()
            # Multi-word phrases: substring check is safe
            if ' ' in _v_clean:
                if _v_clean in ql:
                    return "analytics"
            else:
                # Single words: use word boundary
                if _re.search(r'\b' + _re.escape(_v_clean) + r'\b', ql):
                    return "analytics"
        # Label-only queries (no feedback context) -> analytics
        # Heuristic: short query, contains trend keyword, lacks feedback markers
        words = ql.split()
        feedback_markers = ['customer', 'owner', 'retailer', 'asking', 'selling',
                            'want', 'saying', 'buying', 'said', 'told', 'shop',
                            'store', 'come', 'asked', 'request', 'demand', 'i ',
                            'we ', 'they ', 'he ', 'she ', 'people', 'students',
                            'visited', 'visit', 'today', 'yesterday', 'eaters',
                            'buyers', 'drinkers', 'kids', 'children', 'family',
                            'families', 'rejecting', 'preferring', 'switched',
                            'switching', 'now ', 'are ', 'is ', 'were ', 'was ',
                            'more ', 'less ', 'from ', 'because', 'these days',
                            'nowadays', 'lately', 'recently', 'noticed', 'observed']
        has_feedback_marker = any(m in ql for m in feedback_markers)
        has_trend_kw = any(tk in ql for tk in TREND_KEYWORDS)
        # Filter dimensions: city, season, festival keywords
        _cities = ['bangalore','hyderabad','mumbai','delhi','chennai','kolkata','pune',
                   'jaipur','ahmedabad','chandigarh','lucknow','bhopal','nagpur','patna','surat']
        _seasons = ['winter','summer','monsoon']
        _festivals = ['diwali','deepavali','holi','onam','ramadan','ramzan','eid','bakrid',
                      'christmas','pongal','sankranti','navratri','dussehra','dasara',
                      'vijayadashami','rakhi','raksha bandhan','ganesh chaturthi',
                      'janmashtami','ugadi','gudi padwa','baisakhi','chhath']
        has_filter_dim = (
            any(c in ql for c in _cities)
            or any(s in ql for s in _seasons)
            or any(f in ql for f in _festivals)
        )
        # Priority order:
        # 1. Trend + filter dimension + NO feedback markers -> analyst query (analytics)
        #    Works for any length: "tangy sour in winter", "regional flavor kolkata"
        if has_trend_kw and has_filter_dim and not has_feedback_marker:
            return "analytics"
        # 2. Short label-only queries -> analytics
        if len(words) <= 4 and has_trend_kw and not has_feedback_marker:
            return "analytics"
        # 3. Default -> classification
        return "classification"

    @st.cache_data
    def _load_dataset():
        import pandas as pd
        return pd.read_csv("data/dataset.csv", keep_default_na=False)

    def _run_analytics(query: str):
        """Option B: text-to-pandas via /generate, with rule-based fallback."""
        import json as _json
        import requests as _requests

        _VALID_COLUMNS = [
            "record_id", "visit_date", "month", "week_number", "quarter", "season",
            "city", "store_type", "retailer_id", "salesperson_name",
            "consumer_demographic", "product_category", "retailer_feedback",
            "trend_signal_type", "trend_label",
        ]
        _VALID_OPS = ["count", "list", "top", "compare"]
        _FESTIVAL_MONTHS = {
            "diwali": [10, 11], "deepavali": [10, 11], "dussehra": [10], "dasara": [10],
            "holi": [3], "onam": [8, 9], "navratri": [10], "christmas": [12],
            "pongal": [1], "sankranti": [1], "eid": [3, 4], "bakrid": [6],
            "rakhi": [8], "raksha bandhan": [8], "ganesh chaturthi": [8, 9],
        }

        def _spec_prompt(question, valid_trends):
            return (
                "You output ONLY one line of JSON. No prose, no markdown.\n"
                "Map the question to filters using these column names exactly: "
                "season, city, store_type, consumer_demographic, product_category, month, quarter, trend_label.\n"
                "operation is one of: count, list, top, compare.\n\n"
                "Q: what trends show up for makhana\n"
                'A: {"filters": {"product_category": "makhana"}, "group_by": null, "operation": "top", "target": "trend_label"}\n'
                "Q: trends among senior citizens\n"
                'A: {"filters": {"consumer_demographic": "senior citizens"}, "group_by": null, "operation": "top", "target": "trend_label"}\n'
                "Q: what sells during Diwali\n"
                'A: {"filters": {"month": "diwali"}, "group_by": null, "operation": "top", "target": "trend_label"}\n'
                "Q: top trends in kirana stores\n"
                'A: {"filters": {"store_type": "Kirana Store"}, "group_by": null, "operation": "top", "target": "trend_label"}\n'
                "Q: list spicy notes in Hyderabad\n"
                'A: {"filters": {"trend_label": "rising_spicy_flavor_preference", "city": "Hyderabad"}, "group_by": null, "operation": "list", "target": "retailer_feedback"}\n'
                "Q: list spicy notes among teenagers\n"
                'A: {"filters": {"trend_label": "rising_spicy_flavor_preference", "consumer_demographic": "teenagers"}, "group_by": null, "operation": "list", "target": "retailer_feedback"}\n'
                "Q: sugar free demand in winter\n"
                'A: {"filters": {"trend_label": "sugar_free_demand", "season": "Winter"}, "group_by": "city", "operation": "count", "target": "trend_label"}\n'
                "Q: sugar free demand among senior citizens in kirana stores in winter\n"
                'A: {"filters": {"trend_label": "sugar_free_demand", "consumer_demographic": "senior citizens", "store_type": "Kirana Store", "season": "Winter"}, "group_by": "city", "operation": "count", "target": "trend_label"}\n'
                "Q: protein snacks among teenagers in supermarkets in summer\n"
                'A: {"filters": {"trend_label": "protein_snack_trend", "consumer_demographic": "teenagers", "store_type": "Supermarket", "season": "Summer"}, "group_by": "city", "operation": "count", "target": "trend_label"}\n'
                "Q: " + question + "\n"
                "A:"
            )

        def _parse_spec(raw):
            txt = raw.strip().replace("```json", "").replace("```", "")
            if "JSON:" in txt:
                txt = txt.split("JSON:")[-1]
            start = txt.find("{")
            if start == -1:
                raise ValueError("no json")
            depth, end = 0, -1
            for i in range(start, len(txt)):
                if txt[i] == "{":
                    depth += 1
                elif txt[i] == "}":
                    depth -= 1
                    if depth == 0:
                        end = i
                        break
            if end == -1:
                raise ValueError("unbalanced json")
            return _json.loads(txt[start:end + 1])

        def _validate_spec(spec):

            # --- VALUE RE-HOMING: snap every model value onto a real column ---
            import difflib as _difflib
            _df_rh = _load_dataset()
            _colvals = {
                _c: list(_df_rh[_c].astype(str).unique())
                for _c in ["city", "store_type", "consumer_demographic",
                           "product_category", "season", "trend_label"]
            }
            _trend_syn_rh = {
                "spicy": "rising_spicy_flavor_preference", "spicy snacks": "rising_spicy_flavor_preference",
                "spice": "rising_spicy_flavor_preference", "sugar free": "sugar_free_demand",
                "sugarfree": "sugar_free_demand", "sugar-free": "sugar_free_demand",
                "diabetic": "sugar_free_demand", "protein": "protein_snack_trend",
                "tangy": "tangy_sour_flavor_rise", "sour": "tangy_sour_flavor_rise",
                "fusion": "fusion_flavor_adoption", "regional": "regional_flavor_revival",
                "western": "western_snack_influence", "gifting": "festive_gifting_trend",
                "festive": "festive_gifting_trend", "vegan": "plant_based_adoption",
                "plant based": "plant_based_adoption", "health": "health_conscious_snacking",
                "healthy": "health_conscious_snacking", "youth": "youth_driven_consumption",
                "online": "online_impulse_buying", "convenience": "convenience_format_preference",
                "small pack": "small_pack_affordability_preference",
                "premium": "premium_packaging_demand", "packaging": "premium_packaging_demand",
                "impulse": "online_impulse_buying", "gym": "protein_snack_trend",
                "affordability": "small_pack_affordability_preference", "cheap": "small_pack_affordability_preference",
                "plant-based": "plant_based_adoption", "sugar-free": "sugar_free_demand",
            }
            _demo_syn_rh = {
                "seniors": "senior citizens", "elderly": "senior citizens", "teens": "teenagers",
                "teenager": "teenagers", "kids": "school children", "children": "school children",
                "families": "middle-income families",
            }
            _fest_rh = {
                "diwali": [10, 11], "deepavali": [10, 11], "holi": [3], "onam": [8, 9],
                "eid": [3, 4], "christmas": [12], "pongal": [1], "sankranti": [1],
                "navratri": [10], "dussehra": [10], "rakhi": [8],
            }

            def _match_in_col(raw, col):
                rl = str(raw).lower().strip()
                vals = _colvals.get(col, [])
                for v in vals:
                    if str(v).lower() == rl:
                        return v
                best, blen = None, 0
                for v in vals:
                    vl = str(v).lower()
                    if vl in rl and len(vl) > blen:
                        best, blen = v, len(vl)
                    elif rl in vl and len(rl) > blen:
                        best, blen = v, len(rl)
                if best is not None:
                    return best
                rt = set(rl.replace("-", " ").split())
                best, bs = None, 0
                for v in vals:
                    ov = len(rt & set(str(v).lower().replace("-", " ").split()))
                    if ov > bs:
                        best, bs = v, ov
                if bs > 0:
                    return best
                c = _difflib.get_close_matches(rl, [str(v).lower() for v in vals], n=1, cutoff=0.82)
                if c:
                    for v in vals:
                        if str(v).lower() == c[0]:
                            return v
                return None

            _raw_filters = spec.get("filters") or {}
            if isinstance(_raw_filters, dict):
                _rehomed = {}
                for _col, _val in _raw_filters.items():
                    _vl = str(_val).lower().strip()
                    if _vl in _trend_syn_rh:
                        _rehomed["trend_label"] = _trend_syn_rh[_vl]; continue
                    _vl_words = _vl.replace("_", " ")
                    _kw_hit = None
                    for _k in sorted(_trend_syn_rh, key=lambda x: -len(x)):
                        if _k in _vl_words:
                            _kw_hit = _trend_syn_rh[_k]; break
                    if _kw_hit is not None and _match_in_col(_val, _col) is None:
                        _rehomed["trend_label"] = _kw_hit; continue
                    if _vl in _fest_rh:
                        _rehomed["month"] = _fest_rh[_vl]; continue
                    if _vl in _demo_syn_rh:
                        _rehomed["consumer_demographic"] = _demo_syn_rh[_vl]; continue
                    _m = _match_in_col(_val, _col) if _col in _colvals else None
                    if _m is not None:
                        _rehomed[_col] = _m; continue
                    _placed = False
                    for _c2 in ["trend_label", "consumer_demographic", "store_type",
                                "city", "product_category", "season"]:
                        _m2 = _match_in_col(_val, _c2)
                        if _m2 is not None:
                            _rehomed[_c2] = _m2; _placed = True; break
                    if not _placed and _col not in _colvals:
                        _rehomed[_col] = _val
                spec["filters"] = _rehomed
            # --- END VALUE RE-HOMING ---
            _aliases = {
                "product": "product_category", "category": "product_category",
                "products": "product_category", "item": "product_category",
                "demographic": "consumer_demographic", "demo": "consumer_demographic",
                "customer": "consumer_demographic", "audience": "consumer_demographic",
                "store": "store_type", "shop": "store_type", "outlet": "store_type",
                "rep": "salesperson_name", "salesperson": "salesperson_name",
                "retailer": "retailer_id", "trend": "trend_label",
                "signal": "trend_signal_type", "date": "visit_date",
            }
            # RESCUE: if the model put column keys at top level instead of in "filters",
            # pull recognised columns into filters.
            _real_cols = {"season","city","store_type","consumer_demographic",
                          "product_category","month","quarter","trend_label",
                          "retailer_id","salesperson_name","week_number","visit_date"}
            _topf = spec.get("filters") or {}
            if not isinstance(_topf, dict):
                _topf = {}
            for _tk in list(spec.keys()):
                if _tk in _real_cols and _tk not in _topf:
                    _topf[_tk] = spec[_tk]
                if _tk in _aliases and _aliases[_tk] in _real_cols and _aliases[_tk] not in _topf:
                    _topf[_aliases[_tk]] = spec[_tk]
            spec["filters"] = _topf
            # TREND SYNONYMS: map loose words to real trend_label values
            _trend_syn = {
                "spicy": "rising_spicy_flavor_preference",
                "spicy notes": "rising_spicy_flavor_preference",
                "spice": "rising_spicy_flavor_preference",
                "sugar free": "sugar_free_demand", "sugarfree": "sugar_free_demand",
                "sugar-free": "sugar_free_demand", "diabetic": "sugar_free_demand",
                "protein": "protein_snack_trend", "gym": "protein_snack_trend",
                "tangy": "tangy_sour_flavor_rise", "sour": "tangy_sour_flavor_rise",
                "fusion": "fusion_flavor_adoption", "regional": "regional_flavor_revival",
                "western": "western_snack_influence", "premium": "premium_packaging_demand",
                "gifting": "festive_gifting_trend", "festive": "festive_gifting_trend",
                "vegan": "plant_based_adoption", "plant based": "plant_based_adoption",
                "health": "health_conscious_snacking", "healthy": "health_conscious_snacking",
                "youth": "youth_driven_consumption", "online": "online_impulse_buying",
                "convenience": "convenience_format_preference",
                "small pack": "small_pack_affordability_preference",
                "affordability": "small_pack_affordability_preference",
            }
            if "trend_label" in spec["filters"]:
                _tv = str(spec["filters"]["trend_label"]).lower().strip()
                if _tv in _trend_syn:
                    spec["filters"]["trend_label"] = _trend_syn[_tv]
            # if 'spicy notes' etc landed in product_category, move to trend_label
            if "product_category" in spec["filters"]:
                _pv = str(spec["filters"]["product_category"]).lower().strip()
                if _pv in _trend_syn:
                    spec["filters"]["trend_label"] = _trend_syn[_pv]
                    del spec["filters"]["product_category"]
            # MONTH NAMES -> month number; QUARTERS -> Q1..Q4; rescue from wrong fields
            _month_map = {
                "january": 1, "jan": 1, "february": 2, "feb": 2, "march": 3, "mar": 3,
                "april": 4, "apr": 4, "may": 5, "june": 6, "jun": 6, "july": 7, "jul": 7,
                "august": 8, "aug": 8, "september": 9, "sep": 9, "sept": 9,
                "october": 10, "oct": 10, "november": 11, "nov": 11,
                "december": 12, "dec": 12,
            }
            _quarter_map = {
                "q1": "Q1", "q2": "Q2", "q3": "Q3", "q4": "Q4",
                "quarter 1": "Q1", "quarter 2": "Q2", "quarter 3": "Q3", "quarter 4": "Q4",
                "first quarter": "Q1", "second quarter": "Q2",
                "third quarter": "Q3", "fourth quarter": "Q4",
            }
            _valid_seasons = {"summer", "monsoon", "winter"}
            _flt = spec.get("filters") or {}
            # If a month name / quarter wrongly landed in 'season', move it out.
            if "season" in _flt:
                _sv = str(_flt["season"]).lower().strip()
                if _sv in _month_map:
                    _flt["month"] = _month_map[_sv]; del _flt["season"]
                elif _sv in _quarter_map:
                    _flt["quarter"] = _quarter_map[_sv]; del _flt["season"]
                elif _sv not in _valid_seasons:
                    # not a real season at all - drop it so it doesn't zero out results
                    del _flt["season"]
            # Normalise an explicit 'month' value that is a name.
            if "month" in _flt:
                _mv = str(_flt["month"]).lower().strip()
                if _mv in _month_map:
                    _flt["month"] = _month_map[_mv]
            # Normalise an explicit 'quarter' value.
            if "quarter" in _flt:
                _qv = str(_flt["quarter"]).lower().strip()
                if _qv in _quarter_map:
                    _flt["quarter"] = _quarter_map[_qv]
            spec["filters"] = _flt
            # remap aliased filter keys to real column names
            _f = spec.get("filters") or {}
            _fixed = {}
            for _k, _v in _f.items():
                _fixed[_aliases.get(_k, _k)] = _v
            spec["filters"] = _fixed
            if spec.get("group_by") in _aliases:
                spec["group_by"] = _aliases[spec["group_by"]]
            if spec.get("target") in _aliases:
                spec["target"] = _aliases[spec["target"]]
            clean = {"filters": {}, "group_by": None, "operation": "count", "target": "trend_label"}
            for col, val in (spec.get("filters") or {}).items():
                if col not in _VALID_COLUMNS:
                    raise ValueError("bad filter col")
                clean["filters"][col] = val
            gb = spec.get("group_by")
            if gb is not None:
                if gb not in _VALID_COLUMNS:
                    raise ValueError("bad group_by")
                clean["group_by"] = gb
            op = spec.get("operation", "count")
            if op not in _VALID_OPS:
                raise ValueError("bad op")
            clean["operation"] = op
            tgt = spec.get("target", "trend_label")
            if tgt not in _VALID_COLUMNS:
                raise ValueError("bad target")
            clean["target"] = tgt
            return clean

        def _run_spec(df, spec):
            import plotly.express as px
            filtered = df.copy()
            applied = []
            for col, val in spec["filters"].items():
                if col == "month" and isinstance(val, str) and val.lower() in _FESTIVAL_MONTHS:
                    months = _FESTIVAL_MONTHS[val.lower()]
                    filtered = filtered[filtered["month"].isin(months)]
                    applied.append(col + " in " + str(months) + " (" + val + ")")
                elif isinstance(val, list):
                    filtered = filtered[filtered[col].isin(val)]
                    applied.append(col + " in " + str(val))
                else:
                    if filtered[col].dtype == object:
                        filtered = filtered[filtered[col].astype(str).str.lower() == str(val).lower()]
                    else:
                        filtered = filtered[filtered[col] == val]
                    applied.append(col + " = " + str(val))

            result = {"text": "", "chart": None, "samples": [], "insight": ""}
            n = len(filtered)
            fdesc = " AND ".join(applied) if applied else "all records"
            if n == 0:
                result["text"] = "No records found for: " + fdesc + "."
                return result
            result["text"] = "Found **" + str(n) + "** records matching: *" + fdesc + "*."

            op, tgt, gb = spec["operation"], spec["target"], spec["group_by"]

            if op == "list":
                cols = [c for c in ["record_id", "city", "consumer_demographic",
                                    "product_category", "retailer_feedback"] if c in filtered.columns]
                _tbl = filtered[cols].head(50).copy()
                _tbl.columns = [c.replace("_", " ").title() for c in _tbl.columns]
                result["list_table"] = _tbl
                result["insight"] = ("Showing <b>" + str(min(50, n)) + "</b> of <b>"
                                     + str(n) + "</b> matching retailer notes below.")
                return result

            if op == "compare" and gb:
                grp = filtered.groupby([gb, "trend_label"]).size().reset_index(name="count")
                fig = px.bar(grp, x=gb, y="count", color="trend_label", barmode="group",
                             title="Comparison by " + gb)
                fig.update_layout(height=400, margin=dict(l=20, r=20, t=50, b=20))
                result["chart"] = fig
            else:
                # Choose a sensible column to chart.
                _bad_cols = {"retailer_feedback", "record_id", "visit_date",
                             "salesperson_name", "retailer_id"}
                chart_col = gb if gb else tgt
                # Never chart free-text/unique columns - they make one bar per row.
                if chart_col in _bad_cols:
                    chart_col = None
                # If the chosen column has only one unique value (uniform result),
                # a single bar is useless - break down by city instead.
                if chart_col is not None and filtered[chart_col].nunique() <= 1:
                    chart_col = None
                if chart_col is None:
                    for _cand in ["city", "consumer_demographic", "store_type",
                                  "season", "trend_label"]:
                        if _cand in filtered.columns and filtered[_cand].nunique() > 1:
                            chart_col = _cand
                            break
                    if chart_col is None:
                        chart_col = "trend_label"
                counts = filtered[chart_col].value_counts().head(12).reset_index()
                counts.columns = [chart_col, "count"]
                # color each bar by its trend family (fallback palette otherwise)
                _fam_color = {}
                for _cat, _labs in LABEL_CATEGORIES.items():
                    for _l in _labs:
                        _fam_color[_l] = CAT_COLORS.get(_cat, "#2563EB")
                _palette_cycle = ["#2563EB", "#10B981", "#8B5CF6", "#EC4899",
                                  "#F59E0B", "#0EA5E9", "#EF4444", "#14B8A6"]
                _bar_colors = []
                for _i, _v in enumerate(counts[chart_col]):
                    _bar_colors.append(_fam_color.get(_v, _palette_cycle[_i % len(_palette_cycle)]))
                _pretty = [str(_v).replace("_", " ").title() for _v in counts[chart_col]]
                import plotly.graph_objects as _go
                fig = _go.Figure(_go.Bar(
                    x=_pretty, y=counts["count"],
                    marker=dict(color=_bar_colors, line=dict(color="white", width=1.5)),
                    text=counts["count"], textposition="outside",
                    textfont=dict(size=18, color="#1E3A8A", family="JetBrains Mono"),
                    cliponaxis=False,
                    hovertemplate="<b>%{x}</b><br>%{y} records<extra></extra>",
                ))
                fig.update_layout(
                    title=dict(text="<b>" + chart_col.replace("_", " ").title() + " Distribution</b>",
                               font=dict(size=19, color="#1E3A8A", family="Inter")),
                    height=460, showlegend=False,
                    margin=dict(l=20, r=20, t=60, b=120),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(239,246,255,0.5)",
                    font=dict(family="Inter", color="#374151", size=13),
                    bargap=0.35,
                    xaxis=dict(tickangle=-35, tickfont=dict(size=12, color="#1E3A8A", family="Inter"),
                               title=None),
                    yaxis=dict(showgrid=True, gridcolor="rgba(37,99,235,0.12)", zeroline=False,
                               title=dict(text="Number of records", font=dict(size=12, color="#9CA3AF")),
                               range=[0, max(counts["count"]) * 1.18]),
                )
                result["chart"] = fig

            _vc = filtered["trend_label"].value_counts()
            if len(_vc):
                _topn = int(_vc.iloc[0])
                _tied = [t for t in _vc.index if int(_vc[t]) == _topn]
                if len(_tied) == 1:
                    tname = _tied[0].replace("_", " ")
                    result["insight"] = ("Across <b>" + str(n) + "</b> records, the dominant trend is <b>"
                                         + tname + "</b> (" + str(_topn) + " records)."
                                         + "<br><br><b>OEM Recommendation:</b> prioritise <b>" + tname
                                         + "</b> initiatives for this segment.")
                else:
                    _names = [t.replace("_", " ") for t in _tied]
                    if len(_names) == 2:
                        _joined = "<b>" + _names[0] + "</b> and <b>" + _names[1] + "</b>"
                    else:
                        _joined = ("<b>" + "</b>, <b>".join(_names[:-1]) + "</b> and <b>"
                                   + _names[-1] + "</b>")
                    result["insight"] = ("Across <b>" + str(n) + "</b> records, "
                                         + str(len(_tied)) + " trends are tied at the top \u2014 "
                                         + _joined + ", each with <b>" + str(_topn) + "</b> records. "
                                         + "No single trend dominates this segment."
                                         + "<br><br><b>OEM Recommendation:</b> monitor these "
                                         + str(len(_tied)) + " trends together, as demand is evenly spread.")
            samples = filtered.sample(min(3, n), random_state=42)
            result["samples"] = samples[["record_id", "city", "consumer_demographic",
                                         "retailer_feedback"]].to_dict("records")
            try:
                result["filtered_df"] = filtered.copy()
            except Exception:
                pass
            try:
                _tt = filtered["trend_label"].value_counts()
                _stats = {
                    "records": int(len(filtered)),
                    "top_trend": _tt.idxmax().replace("_", " ") if len(_tt) else "n/a",
                    "top_trend_n": int(_tt.max()) if len(_tt) else 0,
                    "top_city": filtered["city"].value_counts().idxmax() if "city" in filtered and filtered["city"].nunique() else "n/a",
                    "top_demo": filtered["consumer_demographic"].value_counts().idxmax() if "consumer_demographic" in filtered and filtered["consumer_demographic"].nunique() else "n/a",
                    "top_product": filtered["product_category"].value_counts().idxmax() if "product_category" in filtered and filtered["product_category"].nunique() else "n/a",
                }
                _xp = (
                    "You are a retail analyst. Given these query results, write 2 sentences: "
                    "first interpret what the data shows, second give one concrete OEM recommendation. "
                    "Be specific and use the numbers. No markdown, no bullet points.\n"
                    "Query: " + query + "\n"
                    "Results: " + str(_stats) + "\n"
                    "Analysis:"
                )
                _xr = _requests.post(API_URL + "/generate",
                                     json={"prompt": _xp, "max_new_tokens": 130}, timeout=45)
                _xt = (_xr.json().get("text", "") or "").strip()
                if _xt and len(_xt) > 20:
                    result["ai_explanation"] = _xt
            except Exception:
                pass
            return result

        try:
            df = _load_dataset()
            valid_trends = ", ".join(sorted(df["trend_label"].unique()))
            prompt = _spec_prompt(query, valid_trends)
            r = _requests.post(API_URL + "/generate",
                               json={"prompt": prompt, "max_new_tokens": 160}, timeout=60)
            r.raise_for_status()
            raw = r.json()["text"]
            spec = _validate_spec(_parse_spec(raw))
            out = _run_spec(df, spec)
            if out.get("text", "").startswith("No records") and not spec["filters"]:
                return _run_analytics_rulebased(query)
            return out
        except Exception as _e:
            import traceback as _tb
            return _run_analytics_rulebased(query)

    def _run_analytics_rulebased(query: str):
        import pandas as pd
        import plotly.express as px
        df = _load_dataset()
        ql = query.lower()
        result = {"text": "", "chart": None, "samples": []}

        # Build keyword -> trend mapping (reused for both single + compare)
        keyword_to_trend = {
                'spicy': 'rising_spicy_flavor_preference',
                'spice': 'rising_spicy_flavor_preference',
                'fusion': 'fusion_flavor_adoption',
                'regional': 'regional_flavor_revival',
                'tangy': 'tangy_sour_flavor_rise',
                'sour': 'tangy_sour_flavor_rise',
                'youth': 'youth_driven_consumption',
                'teen': 'youth_driven_consumption',
                'sugar': 'sugar_free_demand',
                'diabetic': 'sugar_free_demand',
                'protein': 'protein_snack_trend',
                'gym': 'protein_snack_trend',
                'plant': 'plant_based_adoption',
                'vegan': 'plant_based_adoption',
                'health': 'health_conscious_snacking',
                'convenience': 'convenience_format_preference',
                'resealable': 'convenience_format_preference',
                'online': 'online_impulse_buying',
                'impulse': 'online_impulse_buying',
                'western': 'western_snack_influence',
                'gifting': 'festive_gifting_trend',
                'festival': 'festive_gifting_trend',
                'premium': 'premium_packaging_demand',
                'packaging': 'premium_packaging_demand',
                'affordability': 'small_pack_affordability_preference',
                'small pack': 'small_pack_affordability_preference',
                'cheap': 'small_pack_affordability_preference',
        }

        # Compare mode detection
        is_compare = any(w in ql for w in [' vs ', ' versus ', 'compare ', ' and '])

        # Direct trend match (full label name in query)
        all_trends_found = []
        for trend in df['trend_label'].unique():
            if trend.lower().replace('_', ' ') in ql or trend.lower() in ql:
                all_trends_found.append(trend)

        # Keyword-based matches (find ALL matches, not just first)
        for kw, t in keyword_to_trend.items():
            if kw in ql and t not in all_trends_found:
                all_trends_found.append(t)

        # Set trend_filter (single mode) or compare_trends (compare mode)
        compare_trends = None
        trend_filter = None
        if is_compare and len(all_trends_found) >= 2:
            compare_trends = all_trends_found[:2]
        elif all_trends_found:
            trend_filter = all_trends_found[0]

        season_filter = None
        for season in ['winter', 'summer', 'monsoon']:
            if season in ql:
                season_filter = season.title()
                break

        # Festival -> month mapping (Indian calendar)
        festival_months = None
        festival_name = None
        festival_to_months = {
            'diwali': (10, 11), 'deepavali': (10, 11), 'dipavali': (10, 11),
            'deepawali': (10, 11), 'lakshmi pooja': (10, 11),
            'holi': (3,), 'holika': (3,), 'phagwah': (3,), 'rangwali': (3,),
            'onam': (8, 9), 'thiruvonam': (8, 9),
            'ramadan': (2, 3), 'ramzan': (2, 3), 'roza': (2, 3),
            'eid': (3, 4), 'eid-ul-fitr': (3, 4), 'eid ul fitr': (3, 4),
            'bakrid': (6,), 'eid-al-adha': (6,), 'bakra eid': (6,),
            'christmas': (12,), 'xmas': (12,), 'x-mas': (12,),
            'pongal': (1,), 'bhogi': (1,), 'mattu pongal': (1,),
            'sankranti': (1,), 'makar sankranti': (1,), 'lohri': (1,),
            'navratri': (10,), 'navaratri': (10,),
            'dussehra': (10,), 'dasara': (10,), 'dussera': (10,),
            'vijayadashami': (10,), 'vijaya dashami': (10,),
            'ayudha pooja': (10,), 'ayudha puja': (10,),
            'rakhi': (8,), 'raksha bandhan': (8,), 'rakshabandhan': (8,),
            'ganesh chaturthi': (8, 9), 'vinayaka chavithi': (8, 9),
            'janmashtami': (8,), 'krishna janmashtami': (8,),
            'gudi padwa': (3, 4), 'ugadi': (3, 4),
            'baisakhi': (4,), 'vaisakhi': (4,),
            'karva chauth': (10,), 'karwa chauth': (10,),
            'chhath': (10, 11), 'chhath puja': (10, 11),
        }
        for fest_kw, months in festival_to_months.items():
            if fest_kw in ql:
                festival_months = months
                festival_name = fest_kw.title()
                break

        city_filter = None
        for city in df['city'].unique():
            if city.lower() in ql:
                city_filter = city
                break

        filtered = df.copy()
        applied_filters = []
        if trend_filter:
            filtered = filtered[filtered['trend_label'] == trend_filter]
            applied_filters.append(f"trend = {trend_filter}")
        if season_filter:
            filtered = filtered[filtered['season'] == season_filter]
            applied_filters.append(f"season = {season_filter}")
        if city_filter:
            filtered = filtered[filtered['city'] == city_filter]
            applied_filters.append(f"city = {city_filter}")
        if festival_months:
            filtered = filtered[filtered['month'].isin(festival_months)]
            applied_filters.append(f"festival = {festival_name} (months {list(festival_months)})")

        if len(filtered) == 0:
            result["text"] = f"No records found for: {', '.join(applied_filters) if applied_filters else 'this query'}."
            return result

        n = len(filtered)
        filter_desc = " AND ".join(applied_filters) if applied_filters else "all records"
        result["text"] = f"Found **{n}** records matching: *{filter_desc}*."

        # Compare mode: 2 trends side-by-side across cities
        if compare_trends:
            sub = df[df['trend_label'].isin(compare_trends)].copy()
            if season_filter: sub = sub[sub['season']==season_filter]
            if city_filter: sub = sub[sub['city']==city_filter]
            grouped = sub.groupby(['city','trend_label']).size().reset_index(name='count')
            t1, t2 = compare_trends
            t1_short = t1.replace('_',' ').title()[:24]
            t2_short = t2.replace('_',' ').title()[:24]
            grouped['trend_short'] = grouped['trend_label'].map({t1: t1_short, t2: t2_short})
            fig = px.bar(grouped, x='city', y='count', color='trend_short', barmode='group',
                         title=f"{t1_short} vs {t2_short} — by city",
                         color_discrete_map={t1_short:'#2563EB', t2_short:'#EA580C'})
            fig.update_layout(height=400, margin=dict(l=20,r=20,t=50,b=20), legend_title_text='Trend')
            result["chart"] = fig
            result["text"] = f"Comparing **{t1}** vs **{t2}** across cities ({len(sub)} total records)."
            # Compare-mode insight
            t1_count = (sub['trend_label']==t1).sum()
            t2_count = (sub['trend_label']==t2).sum()
            leader = t1_short if t1_count >= t2_count else t2_short
            loser = t2_short if t1_count >= t2_count else t1_short
            leader_n = max(t1_count, t2_count)
            loser_n = min(t1_count, t2_count)
            top_city = sub.groupby('city').size().sort_values(ascending=False).head(1)
            top_city_name = top_city.index[0] if len(top_city) else "—"
            top_city_n = top_city.iloc[0] if len(top_city) else 0
            cmp_insight = f"Comparing the two trends across <b>{len(sub)}</b> records, <b>{leader}</b> is the dominant signal with <b>{leader_n}</b> observations vs <b>{loser_n}</b> for <b>{loser}</b>. Activity concentrates most in <b>{top_city_name}</b> with <b>{top_city_n}</b> records."
            cmp_action = f"<b>OEM Recommendation:</b> Prioritize <b>{leader}</b> initiatives, with <b>{top_city_name}</b> as the lead market for rollout."
            result["insight"] = cmp_insight + "<br><br>" + cmp_action
            sample = sub.sample(min(3, len(sub)), random_state=42)
            result["samples"] = sample[['record_id','city','consumer_demographic','retailer_feedback']].to_dict('records')
            return result

        if trend_filter and not (season_filter or city_filter):
            city_counts = filtered['city'].value_counts().reset_index()
            city_counts.columns = ['city', 'count']
            fig = px.bar(city_counts, x='city', y='count', title=f"{trend_filter} — by city")
            fig.update_traces(marker_color='#2563EB')
            fig.update_layout(height=350, showlegend=False, margin=dict(l=20, r=20, t=40, b=20))
            result["chart"] = fig
        elif season_filter and not trend_filter:
            trend_counts = filtered['trend_label'].value_counts().head(10).reset_index()
            trend_counts.columns = ['trend', 'count']
            fig = px.bar(trend_counts, x='count', y='trend', orientation='h',
                         title=f"Top trends in {season_filter}")
            fig.update_traces(marker_color='#0D9488')
            fig.update_layout(height=400, showlegend=False, margin=dict(l=20, r=20, t=40, b=20))
            result["chart"] = fig
        elif city_filter and not trend_filter:
            trend_counts = filtered['trend_label'].value_counts().head(8).reset_index()
            trend_counts.columns = ['trend', 'count']
            fig = px.bar(trend_counts, x='count', y='trend', orientation='h',
                         title=f"Trends in {city_filter}")
            fig.update_traces(marker_color='#7C3AED')
            fig.update_layout(height=350, showlegend=False, margin=dict(l=20, r=20, t=40, b=20))
            result["chart"] = fig
        elif festival_months and not trend_filter:
            # User asked "what sells during X festival" -> show top trends
            trend_counts = filtered['trend_label'].value_counts().reset_index()
            trend_counts.columns = ['trend', 'count']
            fig = px.bar(trend_counts, x='count', y='trend', orientation='h',
                         title=f"Trend distribution during {festival_name} (all {len(trend_counts)} trends)")
            fig.update_traces(marker_color='#EA580C')
            fig.update_layout(height=350, showlegend=False, margin=dict(l=20, r=20, t=40, b=20))
            result["chart"] = fig
        else:
            demo_counts = filtered['consumer_demographic'].value_counts().reset_index()
            demo_counts.columns = ['demographic', 'count']
            fig = px.bar(demo_counts, x='demographic', y='count', title="By demographic")
            fig.update_traces(marker_color='#EA580C')
            fig.update_layout(height=350, showlegend=False, margin=dict(l=20, r=20, t=40, b=20))
            result["chart"] = fig

        # Build natural-sentence insight + recommended action
        total = len(filtered)
        ins_parts = []
        action_parts = []
        # Demographic — lowered threshold for broad queries
        if 'consumer_demographic' in filtered.columns and filtered['consumer_demographic'].nunique() > 1:
            td = filtered['consumer_demographic'].value_counts().head(1)
            pct = (td.iloc[0] / total) * 100
            if pct >= 12:
                ins_parts.append(f"Top demographic is <b>{td.index[0]}</b> at {pct:.0f}%")
                action_parts.append(f"target <b>{td.index[0]}</b> as the lead demographic")
        # Geography — lowered
        if 'city' in filtered.columns and filtered['city'].nunique() > 1:
            tc = filtered['city'].value_counts().head(1)
            pct = (tc.iloc[0] / total) * 100
            if pct >= 10:
                ins_parts.append(f"Top city is <b>{tc.index[0]}</b> at {pct:.0f}%")
                action_parts.append(f"prioritize <b>{tc.index[0]}</b> as the lead market")
        # Product — lowered
        if 'product_category' in filtered.columns and filtered['product_category'].nunique() > 1:
            tp = filtered['product_category'].value_counts().head(1)
            pct = (tp.iloc[0] / total) * 100
            if pct >= 12:
                ins_parts.append(f"Top product category is <b>{tp.index[0]}</b> at {pct:.0f}%")
                action_parts.append(f"lead with <b>{tp.index[0]}</b> SKUs")
        # Store type
        if 'store_type' in filtered.columns and filtered['store_type'].nunique() > 1:
            tst = filtered['store_type'].value_counts().head(1)
            pct = (tst.iloc[0] / total) * 100
            if pct >= 30:
                ins_parts.append(f"observed mainly in <b>{tst.index[0]}</b> outlets")
        # Festival queries: prepend top trend (since chart shows trends)
        if festival_months and not trend_filter and 'trend_label' in filtered.columns:
            tt = filtered['trend_label'].value_counts().head(1)
            tt_name = tt.index[0].replace("_", " ")
            tt_count = int(tt.iloc[0])
            ins_parts.insert(0, f"Top trend is <b>{tt_name}</b> with {tt_count} records")
            action_parts.insert(0, f"lead with <b>{tt_name}</b> as the dominant trend signal")

        # Compose the sentence
        topic_parts = []
        # Natural English opener
        if festival_months and festival_name:
            opener = f"During <b>{festival_name}</b>, the system identified <b>{total}</b> retailer observations in our dataset."
        elif trend_filter and season_filter:
            tf = trend_filter.replace("_", " ")
            opener = f"For the <b>{tf}</b> trend in <b>{season_filter}</b>, we have <b>{total}</b> matching records."
        elif trend_filter:
            tf = trend_filter.replace("_", " ")
            opener = f"For the <b>{tf}</b> trend, the dataset has <b>{total}</b> records."
        elif compare_trends:
            a = compare_trends[0].replace("_", " ")
            b = compare_trends[1].replace("_", " ")
            opener = f"Comparing <b>{a}</b> vs <b>{b}</b>, we have <b>{total}</b> combined records."
        elif season_filter:
            opener = f"During <b>{season_filter}</b>, the system found <b>{total}</b> retailer observations."
        else:
            opener = f"This segment contains <b>{total}</b> records."
        # Findings - natural standalone clauses
        if ins_parts:
            findings = " " + ". ".join(ins_parts) + "."
        else:
            findings = " No single dimension dominates - distribution is fairly even."
        sentence = opener + findings
        # Action
        if action_parts:
            if len(action_parts) >= 3:
                action = "<b>OEM Recommendation:</b> Based on the independent signals — " + "; ".join(action_parts) + "."
            elif len(action_parts) == 2:
                action = "<b>OEM Recommendation:</b> " + action_parts[0] + " and " + action_parts[1] + "."
            else:
                action = "<b>OEM Recommendation:</b> " + action_parts[0] + "."
        else:
            action = "<b>OEM Recommendation:</b> Collect more field samples to identify a clearer pattern."

        result["insight"] = sentence + "<br><br>" + action

        samples = filtered.sample(min(3, len(filtered)), random_state=42)
        result["samples"] = samples[['record_id','city','consumer_demographic','retailer_feedback']].to_dict('records')
        try:
            result["filtered_df"] = filtered.copy()
        except Exception:
            pass
        return result

    def _run_classification(query: str):
        import requests, json as _json
        try:
            r = requests.post("http://localhost:8000/predict",
                              json={"retailer_feedback": query}, timeout=30)
            r.raise_for_status()
            res = r.json()
            res.setdefault("explanation", "")
            res.setdefault("trigger_words", [])
            if not res.get("out_of_scope") and res.get("primary_trend"):
                try:
                    _top = res["primary_trend"].replace("_", " ")
                    _ep = (
                        "You explain a trend classification. Output ONLY one line of JSON, no markdown.\n"
                        "Write a one-sentence reason and list the exact phrases from the feedback that signal the trend.\n"
                        'Format: {"reason": "...", "phrases": ["...", "..."]}\n'
                        "Feedback: " + query + "\n"
                        "Predicted trend: " + _top + "\n"
                        "JSON:"
                    )
                    _er = requests.post("http://localhost:8000/generate",
                                        json={"prompt": _ep, "max_new_tokens": 120}, timeout=40)
                    _et = _er.json().get("text", "")
                    _a, _b = _et.find("{"), _et.rfind("}")
                    if _a != -1 and _b != -1 and _b > _a:
                        _p = _json.loads(_et[_a:_b + 1])
                        res["explanation"] = str(_p.get("reason", "")).strip()
                        _ph = _p.get("phrases", [])
                        res["trigger_words"] = [str(x).strip() for x in _ph if str(x).strip()] if isinstance(_ph, list) else []
                except Exception:
                    pass
                # ===== COUNTERFACTUAL: prove the model reads meaning, not keywords =====
                try:
                    _cf_map = {
                        "rising_spicy_flavor_preference": "Customers want mild, less spicy snacks only.",
                        "sugar_free_demand": "Customers want extra sweet, sugary snacks only.",
                        "premium_packaging_demand": "Customers want cheap basic plastic packaging only.",
                        "small_pack_affordability_preference": "Customers want large premium gift packs only.",
                        "western_snack_influence": "Customers want traditional regional Indian snacks only.",
                        "regional_flavor_revival": "Customers want imported western style snacks only.",
                        "protein_snack_trend": "Customers want sugary indulgent treat snacks only.",
                        "health_conscious_snacking": "Customers want deep fried oily snacks only.",
                        "festive_gifting_trend": "Customers buying small everyday single packs only.",
                        "youth_driven_consumption": "Mostly elderly senior citizens buying these snacks.",
                        "plant_based_adoption": "Customers want dairy and meat based snacks only.",
                        "tangy_sour_flavor_rise": "Customers want plain unsalted bland snacks only.",
                        "convenience_format_preference": "Customers want bulk loose unpackaged snacks only.",
                        "online_impulse_buying": "Customers only buy after careful planned research.",
                        "fusion_flavor_adoption": "Customers want single traditional classic flavors only.",
                        "premium_indulgence_trend": "Customers want cheapest basic value snacks only.",
                    }
                    _cf_text = _cf_map.get(res["primary_trend"])
                    if _cf_text:
                        _cfr = requests.post("http://localhost:8000/predict",
                                             json={"retailer_feedback": _cf_text}, timeout=30)
                        _cfj = _cfr.json()
                        res["counterfactual"] = {
                            "contrast_text": _cf_text,
                            "contrast_trend": _cfj.get("primary_trend", ""),
                            "contrast_conf": _cfj.get("primary_confidence", 0),
                            "flipped": _cfj.get("primary_trend", "") != res["primary_trend"],
                        }
                except Exception:
                    res["counterfactual"] = None
            return res
        except Exception as e:
            return {"error": str(e)}

    st.markdown("""
    <style>
    div[data-testid="stTextInput"] input {
        background: #FFFFFF !important;
        border: 2px solid #2563EB !important;
        border-radius: 12px !important;
        padding: 1rem 1.2rem !important;
        font-size: 1rem !important;
        box-shadow: 0 2px 8px rgba(37, 99, 235, 0.08) !important;
        transition: all 0.2s ease !important;
    }
    div[data-testid="stTextInput"] input:focus {
        border-color: #1D4ED8 !important;
        box-shadow: 0 4px 16px rgba(37, 99, 235, 0.18) !important;
        outline: none !important;
    }
    div[data-testid="stTextInput"] input::placeholder {
        color: #94A3B8 !important;
        font-style: italic !important;
    }
    </style>
    """, unsafe_allow_html=True)
    _mode = st.radio(
        "Mode",
        ["🔍 Classify a retailer note", "📊 Ask an analytics question"],
        horizontal=True, label_visibility="collapsed", key="cte_mode",
    )
    st.markdown('<div style="color:#1F2937;font-size:0.95rem;font-weight:700;margin-bottom:0.4rem;">💬 Type your question or paste a retailer note below:</div>', unsafe_allow_html=True)
    chat_input = st.text_input("Ask anything",
                                placeholder="e.g. 'Customers want spicy snacks' OR 'show me spicy demand in Bangalore'",
                                key=f"chat_input_{st.session_state.get('chat_input_counter', 0)}", label_visibility="collapsed")
    col_a, col_b = st.columns([1, 5])
    with col_a:
        send = st.button("⚡ Send", type="primary", use_container_width=True, key="chat_send_btn")
    with col_b:
        if st.button("🗑️ Clear chat", use_container_width=False, key="chat_clear_btn"):
            st.session_state.chat_history = []
            st.session_state.chat_input_counter = st.session_state.get("chat_input_counter", 0) + 1
            st.rerun()

    if send and chat_input and chat_input.strip():
        intent = "analytics" if st.session_state.get("cte_mode", "").startswith("📊") else "classification"
        if intent == "analytics":
            with st.status("🔍 Analyzing data and generating insights...", expanded=False) as _stat:
                result = _run_analytics(chat_input)
                _stat.update(label="✅ Analysis complete", state="complete")
            st.session_state.chat_history.append({"role": "user", "text": chat_input})
            st.session_state.chat_history.append({"role": "assistant", "intent": "analytics", "result": result, "query": chat_input})
        else:
            with st.status("🧠 Classifying feedback and computing explanation...", expanded=False) as _stat:
                result = _run_classification(chat_input)
                _stat.update(label="✅ Classification complete", state="complete")
            st.session_state.chat_history.append({"role": "user", "text": chat_input})
            st.session_state.chat_history.append({"role": "assistant", "intent": "classification", "result": result, "query": chat_input})

    # Render chat history (newest first)
    for msg in reversed(st.session_state.chat_history):
        if msg["role"] == "user":
            st.markdown(f'<div style="background:#EFF6FF;border-left:4px solid #2563EB;padding:0.8rem 1rem;border-radius:8px;margin:0.8rem 0;"><b>🧑 You:</b> {msg["text"]}</div>', unsafe_allow_html=True)
        else:
            intent = msg.get("intent", "")
            def _render_dashboard(_r):
                import plotly.graph_objects as _go
                import plotly.express as _px
                _PAL = ["#1E40AF", "#2563EB", "#0D9488", "#14B8A6", "#0EA5E9", "#3B82F6", "#0891B2", "#5EEAD4"]
                _SCALE = [[0, "#DBEAFE"], [0.5, "#2563EB"], [1, "#0D9488"]]
                _fdf = _r.get("filtered_df")
                if _fdf is None or len(_fdf) == 0:
                    if _r.get("chart") is not None:
                        st.plotly_chart(_r["chart"], use_container_width=True, config={"displayModeBar": False})
                    return
                _n = len(_fdf)
                _top_trend = _fdf["trend_label"].value_counts().idxmax().replace("_", " ").title() if "trend_label" in _fdf else "-"
                _top_city = _fdf["city"].value_counts().idxmax() if "city" in _fdf and _fdf["city"].nunique() else "-"
                _top_demo = _fdf["consumer_demographic"].value_counts().idxmax() if "consumer_demographic" in _fdf and _fdf["consumer_demographic"].nunique() else "-"
                # METRIC CARDS
                _c1, _c2, _c3, _c4 = st.columns(4)
                _card = lambda v, l, col: f'<div style="background:linear-gradient(135deg,{col}15,{col}05);border:1px solid {col}30;border-radius:14px;padding:1rem 1.1rem;text-align:center;"><div style="font-size:1.6rem;font-weight:800;color:{col};line-height:1.1;">{v}</div><div style="font-size:0.72rem;color:#64748B;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;margin-top:0.3rem;">{l}</div></div>'
                _c1.markdown(_card(_n, "Records", "#2563EB"), unsafe_allow_html=True)
                _c2.markdown(_card(_top_trend, "Top Trend", "#10B981"), unsafe_allow_html=True)
                _c3.markdown(_card(_top_city, "Top City", "#8B5CF6"), unsafe_allow_html=True)
                _c4.markdown(_card(_top_demo, "Top Segment", "#EC4899"), unsafe_allow_html=True)
                st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)
                # ROW: trend bar + trend donut
                _g1, _g2 = st.columns([3, 2])
                _tc = _fdf["trend_label"].value_counts().head(10).reset_index()
                _tc.columns = ["trend_label", "count"]
                _tc["Category"] = _tc["trend_label"].apply(get_category)
                _tc["trend"] = _tc["trend_label"].str.replace("_", " ").str.title()
                with _g1:
                    _f = _px.bar(_tc, x="count", y="trend", orientation="h", title="Trend Distribution")
                    _f.update_traces(marker_color="#2563EB")
                    _f.update_layout(height=340, margin=dict(l=10,r=10,t=40,b=10), showlegend=False,
                                     yaxis=dict(autorange="reversed", title=None), xaxis_title=None,
                                     paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(239,246,255,0.4)",
                                     font=dict(family="Inter", size=12), title_font=dict(size=15, color="#1E3A8A"))
                    st.plotly_chart(_f, use_container_width=True, config={"displayModeBar": False})
                with _g2:
                    _d = _px.pie(_tc.head(6), values="count", names="trend", hole=0.55, title="Trend Share", color_discrete_sequence=["#4D7C0F","#65A30D","#84CC16","#A3E635","#BEF264","#D9F99D"])
                    _d.update_layout(height=340, margin=dict(l=10,r=10,t=40,b=10), showlegend=False,
                                     paper_bgcolor="rgba(0,0,0,0)", font=dict(family="Inter", size=11),
                                     title_font=dict(size=15, color="#1E3A8A"))
                    _d.update_traces(textposition="inside", textinfo="percent")
                    st.plotly_chart(_d, use_container_width=True, config={"displayModeBar": False})
                # ROW: city + demographic breakdown
                _g3, _g4 = st.columns(2)
                if "city" in _fdf and _fdf["city"].nunique() > 1:
                    _cc = _fdf["city"].value_counts().head(8).reset_index()
                    _cc.columns = ["city", "count"]
                    with _g3:
                        _city_pal = ["#3B82F6","#EAB308","#9333EA","#EC4899","#14B8A6","#EF4444","#0EA5E9","#F97316"]
                        _f3 = _px.bar(_cc, x="city", y="count", title="By City")
                        _f3.update_traces(marker_color="#EAB308")
                        _f3.update_layout(showlegend=False)
                        _f3.update_layout(height=300, margin=dict(l=10,r=10,t=40,b=10),
                                          xaxis_title=None, yaxis_title=None, paper_bgcolor="rgba(0,0,0,0)",
                                          plot_bgcolor="rgba(239,246,255,0.4)", font=dict(family="Inter", size=11),
                                          title_font=dict(size=15, color="#1E3A8A"))
                        st.plotly_chart(_f3, use_container_width=True, config={"displayModeBar": False})
                if "consumer_demographic" in _fdf and _fdf["consumer_demographic"].nunique() > 1:
                    _dc = _fdf["consumer_demographic"].value_counts().head(8).reset_index()
                    _dc.columns = ["demo", "count"]
                    with _g4:
                        _f4 = _px.bar(_dc, x="count", y="demo", orientation="h", title="By Demographic")
                        _f4.update_traces(marker_color="#9333EA")
                        _f4.update_layout(height=300, margin=dict(l=10,r=10,t=40,b=10), showlegend=False,
                                          yaxis=dict(autorange="reversed", title=None), xaxis_title=None,
                                          paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(239,246,255,0.4)",
                                          font=dict(family="Inter", size=11), title_font=dict(size=15, color="#1E3A8A"))
                        st.plotly_chart(_f4, use_container_width=True, config={"displayModeBar": False})
                # BY PRODUCT
                if "product_category" in _fdf and _fdf["product_category"].nunique() > 1:
                    _pc = _fdf["product_category"].value_counts().head(10).reset_index()
                    _pc.columns = ["product", "count"]
                    _pc["product"] = _pc["product"].str.title()
                    _prod_pal = ["#9333EA","#EAB308","#EC4899","#EF4444","#3B82F6","#14B8A6","#0EA5E9","#F97316","#8B5CF6","#10B981"]
                    _fp = _px.bar(_pc, x="product", y="count", title="By Product")
                    _fp.update_traces(marker_color="#EC4899")
                    _fp.update_layout(height=300, margin=dict(l=10,r=10,t=40,b=10), showlegend=False,
                                      xaxis_title=None, yaxis_title=None, paper_bgcolor="rgba(0,0,0,0)",
                                      plot_bgcolor="rgba(239,246,255,0.4)", font=dict(family="Inter", size=11),
                                      title_font=dict(size=15, color="#1E3A8A"))
                    st.plotly_chart(_fp, use_container_width=True, config={"displayModeBar": False})

            if intent == "analytics":
                r = msg["result"]
                st.markdown(f'<div style="background:#F0FDF4;border-left:4px solid #10B981;padding:0.8rem 1rem;border-radius:8px;margin:0.5rem 0;"><b>📊 Analytics:</b> {r["text"]}</div>', unsafe_allow_html=True)
                if r.get("list_table") is not None:
                    st.dataframe(r["list_table"], use_container_width=True, hide_index=True)
                if r.get("filtered_df") is not None and len(r.get("filtered_df")) > 0:
                    _render_dashboard(r)
                elif r.get("chart") is not None:
                    st.plotly_chart(r["chart"], use_container_width=True, config={"displayModeBar": False})
                if r.get("ai_explanation"):
                    st.markdown(f'<div style="background:linear-gradient(135deg,#EEF2FF,#F5F3FF);border-left:5px solid #6366F1;padding:1.2rem 1.4rem;border-radius:10px;margin:1rem 0;box-shadow:0 2px 8px rgba(99,102,241,0.10);"><div style="color:#4338CA;font-size:1rem;font-weight:800;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.7rem;">🤖 AI Analysis</div><div style="color:#1F2937;font-size:1.05rem;line-height:1.75;">{r["ai_explanation"]}</div></div>', unsafe_allow_html=True)
                if r.get("insight") and not r.get("ai_explanation"):
                    st.markdown(f'<div style="background:#FFFBEB;border-left:5px solid #F59E0B;padding:1.2rem 1.4rem;border-radius:10px;margin:1rem 0;"><div style="color:#92400E;font-size:1rem;font-weight:800;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.7rem;">📌 Key Findings</div><div style="color:#1F2937;font-size:1.05rem;line-height:1.75;">{r["insight"]}</div></div>', unsafe_allow_html=True)
                if r.get("samples"):
                    st.markdown('<div style="color:#9CA3AF;font-size:0.78rem;font-weight:600;margin-top:1rem;margin-bottom:0.3rem;text-transform:uppercase;letter-spacing:0.05em;">📎 Supporting evidence — 3 sample notes from the filtered records</div>', unsafe_allow_html=True)
                    for s in r["samples"]:
                        st.markdown(f'<div style="background:#FAFAFA;border:1px solid #E5E7EB;padding:0.5rem 0.8rem;border-radius:6px;margin:0.25rem 0;font-size:0.82rem;color:#6B7280;"><b style="color:#374151;">{s["record_id"]}</b> · {s["city"]} · {s["consumer_demographic"]}<br><i>"{s["retailer_feedback"]}"</i></div>', unsafe_allow_html=True)
            else:
                r = msg["result"]
                if "error" in r:
                    st.markdown(f'<div style="background:#FEF2F2;border-left:4px solid #DC2626;padding:0.8rem 1rem;border-radius:8px;margin:0.5rem 0;"><b>❌ Error:</b> {r["error"]}</div>', unsafe_allow_html=True)
                elif r.get("out_of_scope"):
                    st.markdown(f'<div style="background:linear-gradient(135deg,#DC2626 0%,#991B1B 100%);color:white;padding:1rem;border-radius:8px;margin:0.5rem 0;"><b>⚠️ OUT OF SCOPE</b><br>Note does not fit trained categories ({r["primary_confidence"]*100:.1f}% top match — below threshold)</div>', unsafe_allow_html=True)
                else:
                    _ptrend = r["primary_trend"]
                    _pconf = r["primary_confidence"]
                    _cat = get_category(_ptrend)
                    st.markdown(f"""
                    <div class="result-card" style="margin:0.5rem 0;">
                        <div class="result-rank">🥇 Primary Trend</div>
                        <div class="result-trend">{_ptrend}</div>
                        <div class="result-conf">{_pconf*100:.1f}%</div>
                        <div class="result-conf-lbl">confidence score</div>
                        <div style="margin-top:0.8rem;">
                            <span style="background:rgba(255,255,255,0.15);border:1.5px solid rgba(255,255,255,0.3);
                            color:#FFFFFF;padding:0.3rem 0.9rem;border-radius:20px;font-size:0.85rem;font-weight:700;">
                            📂 {_cat}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    _model_exp = (r.get("explanation") or "").strip()
                    _exp = _model_exp or TREND_EXPLANATIONS.get(_ptrend, "") or "This trend was inferred from the retailer feedback signals."
                    _why_title = _ptrend.replace("_", " ").title()
                    _fb_text = msg.get("query", "")
                    st.markdown(f"""
                    <div class="explain-box" style="margin-top:0.8rem;margin-bottom:0.8rem;">
                        <div class="explain-title">💡 Why {_why_title}?</div>
                        <div class="explain-text">{_exp}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.plotly_chart(make_bar_chart(r), use_container_width=True, config={"displayModeBar":False}, key=f"chat_chart_{msg.get('query','')}_{_ptrend}")
                    _oem = OEM_ACTIONS.get(_ptrend, "Review trend signal and initiate NPD discussion.")
                    st.markdown(f"""
                    <div class="oem-card">
                        <div class="oem-title">💡 OEM Action Recommendation</div>
                        <div class="oem-text">{_oem}</div>
                    </div>
                    """, unsafe_allow_html=True)


with tab3:
    st.markdown('<div class="sec-label">📝 Quick Batch — Paste Multiple Notes</div>', unsafe_allow_html=True)
    st.markdown('<div style="color:#9CA3AF;font-size:0.95rem;margin-bottom:0.6rem;">Paste one retailer note per line, then classify all at once.</div>', unsafe_allow_html=True)
    def _clear_paste():
        st.session_state["paste_notes"] = ""
    paste_txt = st.text_area("Paste notes (one per line)", height=160, key="paste_notes",
        placeholder="Customers asking for extra spicy snacks only\nDiabetic buyers want sugar-free namkeen\nRs.5 and Rs.10 packs selling most")
    _bc1, _bc2 = st.columns([2,1])
    with _bc1:
        _run_paste = st.button("⚡  Classify All Pasted Notes", type="primary", key="paste_run", use_container_width=True)
    with _bc2:
        st.button("Clear", key="paste_clear", on_click=_clear_paste, use_container_width=True)
    if _run_paste:
        notes = [ln.strip() for ln in paste_txt.split("\n") if ln.strip()]
        if not notes:
            st.warning("Please paste at least one note.")
        else:
            rows = []
            prog = st.progress(0); status = st.empty()
            for i, note in enumerate(notes):
                status.markdown(f'<div style="color:#2563EB;font-size:0.95rem;">Processing {i+1}/{len(notes)}...</div>', unsafe_allow_html=True)
                prog.progress((i+1)/len(notes))
                res = call_predict(api_url, note)
                if res:
                    rows.append({"retailer_feedback": note[:60], "primary_trend": res["primary_trend"],
                        "confidence_%": round(res["primary_confidence"]*100,1),
                        "category": get_category(res["primary_trend"])})
                else:
                    rows.append({"retailer_feedback": note[:60], "primary_trend":"ERROR","confidence_%":0,"category":"Error"})
            status.empty(); prog.empty()
            pdf = pd.DataFrame(rows)
            st.success(f"✅ Classified {len(rows)} notes")
            st.dataframe(pdf, use_container_width=True)
            cat_counts = pdf["category"].value_counts().to_dict()
            st.plotly_chart(make_donut(cat_counts), use_container_width=True, config={"displayModeBar":False})

    st.markdown('<div style="border-top:1px solid #E2E8F0;margin:1.5rem 0;"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-label">📂 Batch CSV Processing</div>', unsafe_allow_html=True)
    col_x, col_y = st.container(), st.container()
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
        try:
            with open("data/sample_batch_50.csv") as _sf:
                sample = _sf.read()
        except Exception:
            sample = "retailer_feedback,city,store_id\nMild variants not moving. Customers asking for extra spicy.,Bhopal,BHO001\n"
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
                        with st.expander("📋  View raw predictions table", expanded=False):
                            st.dataframe(final, use_container_width=True, hide_index=True)
                        cat_counts = final["category"].value_counts().to_dict()
                        # ===== FIELD INTELLIGENCE LAYER =====
                        import plotly.express as _bpx
                        _n = len(final)
                        _flagged = int(((final["primary_trend"] == "OUT_OF_SCOPE") | (final["primary_trend"] == "ERROR")).sum())
                        _valid = final[(final["primary_trend"] != "ERROR") & (final["primary_trend"] != "OUT_OF_SCOPE")]
                        _dom = _valid["primary_trend"].value_counts().idxmax().replace("_"," ").title() if len(_valid) else "n/a"
                        _ndistinct = _valid["primary_trend"].nunique()
                        _avgconf = round(_valid["primary_conf_%"].mean(),1) if len(_valid) else 0
                        st.markdown('<div class="sec-label" style="margin-top:1.5rem;">\U0001F4E1 Field Intelligence Summary</div>', unsafe_allow_html=True)
                        _b1,_b2,_b3,_b4 = st.columns(4)
                        _bcard = lambda v,l,c,fs="1.5rem": f'<div style="background:linear-gradient(135deg,{c}15,{c}05);border:1px solid {c}30;border-radius:14px;padding:1rem;text-align:center;min-height:90px;display:flex;flex-direction:column;justify-content:center;"><div style="font-size:{fs};font-weight:800;color:{c};line-height:1.2;">{v}</div><div style="font-size:0.7rem;color:#64748B;font-weight:700;text-transform:uppercase;margin-top:0.3rem;">{l}</div></div>'
                        _b1.markdown(_bcard(_n,"Reports","#2563EB"), unsafe_allow_html=True)
                        _b2.markdown(_bcard(_dom,"Dominant Trend","#0D9488","1.05rem"), unsafe_allow_html=True)
                        _b3.markdown(_bcard(_ndistinct,"Distinct Trends","#9333EA"), unsafe_allow_html=True)
                        _b4.markdown(_bcard(f"{_avgconf}%","Avg Confidence","#EC4899"), unsafe_allow_html=True)
                        st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)
                        # Trend distribution across all reports
                        _tdist = _valid["primary_trend"].value_counts().reset_index()
                        _tdist.columns = ["trend","count"]
                        _tdist["trend"] = _tdist["trend"].str.replace("_"," ").str.title()
                        if _flagged > 0:
                            st.markdown(f'<div style="background:#FEF3C7;border-left:4px solid #F59E0B;padding:0.6rem 1rem;border-radius:8px;margin:0.5rem 0;font-size:0.9rem;color:#92400E;">⚠️ <b>{_flagged}</b> report(s) flagged for human review (low confidence or out of scope) — excluded from the trend landscape below.</div>', unsafe_allow_html=True)
                        _bfig = _bpx.bar(_tdist, x="count", y="trend", orientation="h", title="Trend Landscape Across All Field Reports")
                        _bfig.update_traces(marker_color="#2563EB")
                        _bfig.update_layout(height=max(300,32*len(_tdist)), margin=dict(l=10,r=10,t=45,b=10),
                                            yaxis=dict(autorange="reversed",title=None), xaxis_title="Number of reports",
                                            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(239,246,255,0.4)",
                                            font=dict(family="Inter",size=12), title_font=dict(size=15,color="#1E3A8A"))
                        st.plotly_chart(_bfig, use_container_width=True, config={"displayModeBar":False})
                        # AI field summary
                        try:
                            import requests as _breq
                            _bstats = {"total_reports": _n, "dominant_trend": _dom,
                                       "distinct_trends": int(_ndistinct),
                                       "top_3": _valid["primary_trend"].value_counts().head(3).to_dict()}
                            _bprompt = ("You are an FMCG field intelligence analyst. Given aggregated trend "
                                        "classifications from multiple retailer field reports, write 2-3 sentences "
                                        "summarizing the collective signal and one strategic recommendation. "
                                        "Use the numbers. No markdown.\n"
                                        "Aggregate: " + str(_bstats) + "\nSummary:")
                            _bres = _breq.post(api_url + "/generate", json={"prompt": _bprompt, "max_new_tokens": 150}, timeout=45)
                            _btext = (_bres.json().get("text","") or "").strip()
                            if _btext and len(_btext) > 20:
                                st.markdown(f'<div style="background:linear-gradient(135deg,#EEF2FF,#F5F3FF);border-left:5px solid #6366F1;padding:1.2rem 1.4rem;border-radius:10px;margin:1rem 0;"><div style="color:#4338CA;font-size:1rem;font-weight:800;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.7rem;">\U0001F916 AI Field Summary</div><div style="color:#1F2937;font-size:1.05rem;line-height:1.75;">{_btext}</div></div>', unsafe_allow_html=True)
                        except Exception:
                            pass
                        st.download_button("⬇  Download Results", data=final.to_csv(index=False),
                            file_name="cte_batch_results.csv", mime="text/csv", use_container_width=True)

st.markdown("""
<div style="margin-top:3rem;padding:1.5rem 0;border-top:2px solid #BFDBFE;
     display:flex;justify-content:space-between;flex-wrap:wrap;gap:0.5rem;">
    <div style="color:#374151;font-size:0.95rem;font-weight:500;">Consumer Trend Extraction · Gemma 2B IT + QLoRA · Field Intelligence Platform</div>
    <div style="color:#374151;font-size:0.95rem;font-weight:500;">Deterministic greedy decoding · 15 trend labels · FastAPI backend</div>
</div>
""", unsafe_allow_html=True)
