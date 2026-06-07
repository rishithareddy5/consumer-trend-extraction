"""
model/preprocess.py
Reads dataset.csv and converts to train.jsonl and test.jsonl
80/20 stratified split
"""
import json
import pandas as pd
from pathlib import Path

ROOT       = Path(__file__).resolve().parent.parent
DATA_DIR   = ROOT / "data"
CSV_PATH   = DATA_DIR / "dataset.csv"
TRAIN_PATH = DATA_DIR / "train.jsonl"
TEST_PATH  = DATA_DIR / "test.jsonl"

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
trend into EXACTLY ONE of these 16 labels:

rising_spicy_flavor_preference | youth_driven_consumption | fusion_flavor_adoption
western_snack_influence | health_conscious_snacking | premium_packaging_demand
regional_flavor_revival | convenience_format_preference | festive_gifting_trend
online_impulse_buying | sugar_free_demand | protein_snack_trend
small_pack_affordability_preference | plant_based_adoption | tangy_sour_flavor_rise | no_trend_detected

Rules:
- Output ONLY valid JSON. No explanation, no extra text.
- Format: {"retailer_feedback": "...", "trend": "..."}
- trend MUST be exactly one label. Never invent new labels."""


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


def split_dataset(df):
    """Manual 80/20 stratified split without sklearn"""
    train_records = []
    test_records  = []
    for trend in df["trend_label"].unique():
        trend_df = df[df["trend_label"] == trend].sample(frac=1, random_state=42)
        split    = int(len(trend_df) * 0.8)
        train_records.append(trend_df.iloc[:split])
        test_records.append(trend_df.iloc[split:])
    return pd.concat(train_records), pd.concat(test_records)


def write_jsonl(df, path):
    with open(path, "w", encoding="utf-8") as f:
        for _, row in df.iterrows():
            f.write(json.dumps(row_to_sample(row), ensure_ascii=False) + "\n")


def convert():
    print(f"[preprocess] Reading CSV: {CSV_PATH}")
    df = pd.read_csv(CSV_PATH)
    print(f"[preprocess] Records: {len(df)}")
    print(f"[preprocess] Columns: {list(df.columns)}")

    train_df, test_df = split_dataset(df)
    print(f"[preprocess] Train: {len(train_df)} | Test: {len(test_df)}")

    write_jsonl(train_df, TRAIN_PATH)
    write_jsonl(test_df,  TEST_PATH)

    print(f"[preprocess] Train → {TRAIN_PATH}")
    print(f"[preprocess] Test  → {TEST_PATH}")
    print("[preprocess] Done!")


if __name__ == "__main__":
    convert()
