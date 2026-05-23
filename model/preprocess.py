"""
model/preprocess.py
Converts Excel dataset → JSONL for Gemma fine-tuning.
Run: python model/preprocess.py
"""
import json
import pandas as pd
from pathlib import Path

ROOT       = Path(__file__).resolve().parent.parent
EXCEL_PATH = ROOT / "data" / "Consumer_Trend_Extraction_Dataset.xlsx"
JSONL_PATH = ROOT / "data" / "batch1_500.jsonl"

VALID_TRENDS = [
    "rising_spicy_flavor_preference","youth_driven_consumption",
    "fusion_flavor_adoption","western_snack_influence",
    "health_conscious_snacking","premium_packaging_demand",
    "regional_flavor_revival","convenience_format_preference",
    "festive_gifting_trend","online_impulse_buying",
    "sugar_free_demand","protein_snack_trend",
    "small_pack_affordability_preference","plant_based_adoption",
    "tangy_sour_flavor_rise",
]

SYSTEM_PROMPT = """You are a consumer trend analyst for an FMCG company in India.
Analyze retailer feedback from field salespersons and classify the dominant consumer
trend into EXACTLY ONE of these 15 labels:

rising_spicy_flavor_preference | youth_driven_consumption | fusion_flavor_adoption
western_snack_influence | health_conscious_snacking | premium_packaging_demand
regional_flavor_revival | convenience_format_preference | festive_gifting_trend
online_impulse_buying | sugar_free_demand | protein_snack_trend
small_pack_affordability_preference | plant_based_adoption | tangy_sour_flavor_rise

Rules:
- Output ONLY valid JSON. No explanation, no extra text.
- Format: {"retailer_feedback": "...", "trend": "..."}
- trend MUST be exactly one label from the list. Never invent new labels."""


def build_user_message(row):
    return f"""Analyze this retailer feedback and identify the primary consumer trend.

Retailer Feedback: {row['retailer_feedback']}
City: {row['city']} | Store Type: {row['store_type']}
Season: {row['season']} | Consumer Demographic: {row['consumer_demographic']}
Product Category: {row['product_category']}

Respond ONLY with JSON: {{"retailer_feedback": "...", "trend": "..."}}"""


def row_to_sample(row):
    return {
        "messages": [
            {"role": "system",    "content": SYSTEM_PROMPT},
            {"role": "user",      "content": build_user_message(row)},
            {"role": "assistant", "content": json.dumps({
                "retailer_feedback": row["retailer_feedback"],
                "trend": row["trend_label"]
            })},
        ]
    }


def validate(df):
    missing = [c for c in ["retailer_feedback","trend_label","city",
               "store_type","season","consumer_demographic","product_category"]
               if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    invalid = df[~df["trend_label"].isin(VALID_TRENDS)]["trend_label"].unique()
    if len(invalid):
        raise ValueError(f"Invalid trends: {invalid}")
    print(f"  Validation passed — {len(df)} records, {df['trend_label'].nunique()} trends")


def convert():
    print(f"[preprocess] Reading: {EXCEL_PATH}")
    df = pd.read_excel(EXCEL_PATH, sheet_name="Training_Dataset")
    validate(df)
    print(f"[preprocess] Converting to JSONL...")
    JSONL_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(JSONL_PATH, "w", encoding="utf-8") as f:
        for _, row in df.iterrows():
            f.write(json.dumps(row_to_sample(row), ensure_ascii=False) + "\n")
    print(f"[preprocess] Done — {len(df)} records → {JSONL_PATH}")
    print("\nTrend distribution:")
    for trend, count in df["trend_label"].value_counts().items():
        print(f"  {trend:<45} {count}")


if __name__ == "__main__":
    convert()
