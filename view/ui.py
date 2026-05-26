"""
view/ui.py
Consumer Trend Extraction - Streamlit UI.

Run:
    streamlit run view/ui.py --server.port 8501 --server.address 0.0.0.0
"""

from __future__ import annotations

import json
import os
import time

import requests
import streamlit as st

API_URL = os.getenv("CTE_API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Consumer Trend Extraction",
    page_icon="🛒",
    layout="wide",
)

with st.sidebar:
    st.title("Config")
    api_url = st.text_input("FastAPI URL", value=API_URL)
    st.caption("Backend must be running on this URL.")

    st.divider()
    st.subheader("Health")
    if st.button("Check"):
        try:
            r = requests.get(f"{api_url}/health", timeout=5)
            st.json(r.json())
        except Exception as e:
            st.error(f"Cannot reach API: {e}")

    st.divider()
    st.subheader("Known trend labels")
    try:
        labels = requests.get(f"{api_url}/labels", timeout=5).json()["labels"]
        for lab in labels:
            st.caption(f"- {lab}")
    except Exception:
        st.caption("(Could not load labels - API may be down.)")

st.title("Consumer Trend Extraction")
st.markdown(
    "Paste a **retailer field note** (what the sales rep heard at the shop) "
    "and the fine-tuned Gemma 2B model will return the top 3 consumer trends "
    "with confidence scores."
)

EXAMPLES = {
    "- pick an example -": "",
    "Spicy chips (college area)": (
        "College boys near the hostel keep asking for the highest spice level "
        "available. Our regular masala chips are not selling anymore."
    ),
    "Cheesy dip (kids)": (
        "Kids are increasingly asking for cheesy dip flavours. Retailer says "
        "we don't stock any, but they could sell 4-5 packs a day."
    ),
    "Sugar-free biscuits": (
        "Two diabetic customers came in this week asking specifically for "
        "sugar-free biscuits. Owner says he has had 6-7 such queries this month."
    ),
    "Small affordable packs": (
        "Rs.5 and Rs.10 packs are flying off the shelves in this area. "
        "Anything above Rs.20 sits for weeks."
    ),
    "Festive gifting": (
        "With Diwali approaching, retailer is asking for premium gift packs. "
        "Says customers walked in 3 times today asking for ready-to-gift boxes."
    ),
}

choice = st.selectbox("Quick examples", list(EXAMPLES.keys()))
default_text = EXAMPLES[choice]

feedback = st.text_area(
    "Retailer feedback",
    value=default_text,
    height=140,
    placeholder="e.g. Kids increasingly asking for cheesy dip flavours...",
)

col_a, col_b = st.columns([1, 4])
go = col_a.button("Extract trends", type="primary", use_container_width=True)
clear = col_b.button("Clear")
if clear:
    st.rerun()

if go:
    if not feedback or len(feedback.strip()) < 3:
        st.warning("Please enter at least 3 characters of retailer feedback.")
        st.stop()

    with st.spinner("Running Gemma 2B + LoRA adapter..."):
        t0 = time.time()
        try:
            r = requests.post(
                f"{api_url}/predict",
                json={"retailer_feedback": feedback.strip()},
                timeout=120,
            )
            r.raise_for_status()
            result = r.json()
        except requests.exceptions.RequestException as e:
            st.error(f"API call failed: {e}")
            st.stop()
        latency_ms = (time.time() - t0) * 1000

    st.success(f"Done in {latency_ms:.0f} ms")

    st.markdown("### Top trend")
    st.markdown(
        f"**`{result['primary_trend']}`** "
        f"&nbsp;&middot;&nbsp; confidence "
        f"**{result['primary_confidence'] * 100:.1f}%**"
    )

    st.markdown("### Ranked predictions")
    rows = [
        ("Primary",   result["primary_trend"],   result["primary_confidence"]),
        ("Secondary", result["secondary_trend"], result["secondary_confidence"]),
        ("Tertiary",  result["tertiary_trend"],  result["tertiary_confidence"]),
    ]
    for rank, label, conf in rows:
        c1, c2, c3 = st.columns([1, 3, 2])
        c1.write(rank)
        c2.code(label, language=None)
        c3.progress(min(max(conf, 0.0), 1.0), text=f"{conf * 100:.1f}%")

    with st.expander("Raw JSON response"):
        payload = {
            k: result[k]
            for k in (
                "primary_trend",
                "primary_confidence",
                "secondary_trend",
                "secondary_confidence",
                "tertiary_trend",
                "tertiary_confidence",
            )
        }
        st.code(json.dumps(payload, indent=2), language="json")
        st.download_button(
            "Download JSON",
            data=json.dumps(payload, indent=2),
            file_name="trend_prediction.json",
            mime="application/json",
        )

    if result.get("raw_generation"):
        with st.expander("Debug - raw model output"):
            st.text(result["raw_generation"])

st.divider()
st.caption(
    "Gemma 2B IT - QLoRA fine-tuned on 500 retailer field notes - "
    "8Bit AI - Field Intelligence use-case #6"
)
