"""
view/ui.py
Streamlit UI — MVC View layer.
Shows top-3 trends with confidence scores + ChromaDB similar examples.
Run: streamlit run view/ui.py --server.port 8501
"""
import sys
import requests
import streamlit as st
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

st.set_page_config(
    page_title="Consumer Trend Extraction",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

.header-box {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    padding: 2rem 2.5rem; border-radius: 16px;
    margin-bottom: 2rem; color: white;
}
.header-box h1 { font-size: 1.8rem; font-weight: 600; margin: 0; }
.header-box p  { font-size: 0.9rem; opacity: 0.7; margin: 0.3rem 0 0; }

.trend-card {
    background: white; border: 1px solid #e8ecf0;
    border-radius: 12px; padding: 1.2rem 1.5rem;
    margin-bottom: 0.8rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.t-rank  { font-size: 0.72rem; color: #999; text-transform: uppercase; letter-spacing: 0.06em; }
.t-label { font-size: 1rem; font-weight: 600; color: #1a1a2e; margin: 0.2rem 0;
           font-family: 'DM Mono', monospace; }
.t-conf  { font-size: 0.84rem; color: #555; }
.bar-bg  { background: #f0f2f5; border-radius: 99px; height: 6px; margin-top: 0.5rem; }
.bar-fg  { height: 6px; border-radius: 99px; }

.sim-card {
    background: #f8f9fb; border-left: 3px solid #3b82f6;
    padding: 0.8rem 1rem; border-radius: 0 8px 8px 0;
    margin-bottom: 0.6rem; font-size: 0.84rem;
}
.sim-trend { font-weight: 600; color: #1e3a5f; font-family: 'DM Mono', monospace; }
</style>
""", unsafe_allow_html=True)

API = "http://localhost:8000"

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="header-box">
    <h1>📊 Consumer Trend Extraction System</h1>
    <p>Gemma 2B + QLoRA &nbsp;|&nbsp; RAG (ChromaDB + BGE-small) &nbsp;|&nbsp;
       FastAPI + Streamlit &nbsp;|&nbsp; MVC Architecture</p>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📍 Field Visit Context")
    st.caption("Optional — improves accuracy")
    city = st.selectbox("City", ["","Hyderabad","Mumbai","Delhi","Bangalore",
        "Chennai","Kolkata","Pune","Ahmedabad","Jaipur","Lucknow","Kochi","Vizag"])
    store_type = st.selectbox("Store Type", ["","Kirana Store","Supermarket",
        "Hypermarket","General Store","College Canteen","Convenience Store",
        "Medical Store","Wholesale Depot"])
    demographic = st.selectbox("Consumer Demographic", ["","college students",
        "teenagers","school children","urban youth","working professionals",
        "homemakers","health-conscious adults","senior citizens",
        "middle-income families","premium shoppers","rural consumers"])
    season = st.selectbox("Season", ["","Summer","Monsoon","Winter","Festive",
        "Post-Festive","Diwali","Holi","Onam","Ramadan","New Year"])

    st.divider()
    st.markdown("### ℹ️ Problem Statement")
    st.caption("""Changing consumer preferences are often identified too late,
    causing OEMs to lose market momentum and miss emerging consumption trends.""")

    st.divider()
    st.markdown("### 🔧 Tech Stack")
    st.caption("""
    🤖 Gemma 2B + QLoRA (4-bit)
    🔗 PEFT + LoRA fine-tuning
    🔍 BGE-small + ChromaDB (RAG)
    ⚡ FastAPI controller
    📊 MLflow experiment tracking
    """)

# ── Main input ────────────────────────────────────────────────────────────────
st.markdown("### 🗣️ Retailer Feedback")
feedback = st.text_area(
    label="",
    height=140,
    placeholder='e.g. "Kids increasingly asking for cheesy dip flavors. '
                'Competitor launched ghost pepper variant and it is flying off shelves."',
)

col1, col2 = st.columns([1, 6])
with col1:
    run = st.button("🔍 Detect Trend", type="primary", use_container_width=True)

# ── Prediction ────────────────────────────────────────────────────────────────
if run:
    if not feedback.strip():
        st.warning("Please enter retailer feedback.")
    else:
        with st.spinner("Analyzing with Gemma 2B + ChromaDB RAG..."):
            try:
                res = requests.post(f"{API}/predict", json={
                    "retailer_feedback":    feedback,
                    "city":                 city,
                    "store_type":           store_type,
                    "consumer_demographic": demographic,
                    "season":               season,
                }, timeout=120)

                if res.status_code == 200:
                    d = res.json()
                    st.success("✅ Trend detected successfully!")

                    # ── Top 3 trends ──────────────────────────────────────────
                    st.markdown("### 🎯 Top 3 Consumer Trends")
                    st.caption("Speaker requirement: show at least 3 trend confidences")

                    for rank, label, conf, color in [
                        ("1st — Primary",   d["primary_trend"],   d["primary_confidence"],   "#10b981"),
                        ("2nd — Secondary", d["secondary_trend"], d["secondary_confidence"], "#3b82f6"),
                        ("3rd — Tertiary",  d["tertiary_trend"],  d["tertiary_confidence"],  "#f59e0b"),
                    ]:
                        pct = int(conf * 100)
                        st.markdown(f"""
                        <div class="trend-card">
                            <div class="t-rank">{rank}</div>
                            <div class="t-label">{label}</div>
                            <div class="t-conf">{pct}% confidence</div>
                            <div class="bar-bg">
                                <div class="bar-fg" style="width:{pct}%;background:{color}"></div>
                            </div>
                        </div>""", unsafe_allow_html=True)

                    # ── ChromaDB similar examples ─────────────────────────────
                    if d.get("similar_examples"):
                        st.markdown("### 🔍 Similar Past Observations (RAG Context)")
                        st.caption("ChromaDB retrieved these from training data to help Gemma")
                        for i, ex in enumerate(d["similar_examples"], 1):
                            sim = int(ex.get("similarity", 0) * 100)
                            st.markdown(f"""
                            <div class="sim-card">
                                <div class="sim-trend">#{i} → {ex['trend']} &nbsp;({sim}% similar)</div>
                                <div style="margin-top:0.3rem;color:#444">
                                    {ex['feedback'][:170]}...
                                </div>
                            </div>""", unsafe_allow_html=True)

                    # ── JSON output ───────────────────────────────────────────
                    with st.expander("📄 Structured JSON Output"):
                        st.json({
                            "retailer_feedback":    feedback,
                            "primary_trend":        d["primary_trend"],
                            "primary_confidence":   d["primary_confidence"],
                            "secondary_trend":      d["secondary_trend"],
                            "secondary_confidence": d["secondary_confidence"],
                            "tertiary_trend":       d["tertiary_trend"],
                            "tertiary_confidence":  d["tertiary_confidence"],
                        })

                    # ── All 15 confidences ────────────────────────────────────
                    with st.expander("📊 All 15 Trend Confidence Scores"):
                        for trend, conf in sorted(
                            d["all_confidences"].items(),
                            key=lambda x: x[1], reverse=True
                        ):
                            st.markdown(f"`{trend}` — **{int(conf*100)}%**")

                else:
                    st.error(f"API error {res.status_code}: {res.json().get('detail','')}")

            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to API. Make sure FastAPI is running:\n"
                         "`uvicorn controller.api:app --host 0.0.0.0 --port 8000`")
            except requests.exceptions.Timeout:
                st.error("⏳ Request timed out. Model may still be loading.")
            except Exception as e:
                st.error(f"Unexpected error: {str(e)}")
