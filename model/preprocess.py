"""
model/preprocess.py
Converts Excel dataset to JSONL for Gemma fine-tuning.
Splits into train (80%) and test (20%) with stratification.
Run: python model/preprocess.py
"""
import json
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split

ROOT       = Path(__file__).resolve().parent.parent
DATA_DIR   = ROOT / "data"
EXCEL_PATH = DATA_DIR / "Consumer_Trend_Extraction_Dataset.xlsx"
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
trend into EXACTLY ONE of these 15 labels:

rising_spicy_flavor_preference | youth_driven_consumption | fusion_flavor_adoption
western_snack_influence | health_conscious_snacking | premium_packaging_demand
regional_flavor_revival | convenience_format_preference | festive_gifting_trend
online_impulse_buying | sugar_free_demand | protein_snack_trend
small_pack_affordability_preference | plant_based_adoption | tangy_sour_flavor_rise

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


def validate(df):
    required = ["retailer_feedback","trend_label","city",
                "store_type","season","consumer_demographic","product_category"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    invalid = df[~df["trend_label"].isin(VALID_TRENDS)]["trend_label"].unique()
    if len(invalid):
        raise ValueError(f"Invalid trend labels: {invalid}")
    dupes = df.duplicated("retailer_feedback").sum()
    if dupes:
        print(f"  Warning: {dupes} duplicate feedbacks found")
    print(f"  Validation passed — {len(df)} records, {df['trend_label'].nunique()} trends")


def write_jsonl(df, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for _, row in df.iterrows():
            f.write(json.dumps(row_to_sample(row), ensure_ascii=False) + "\n")


def convert():
    print(f"\n[preprocess] Reading: {EXCEL_PATH}")
    df = pd.read_excel(EXCEL_PATH, sheet_name="Training_Dataset")

    print(f"[preprocess] Validating...")
    validate(df)

    # ── Stratified split — equal class representation in both splits ──────────
    train_df, test_df = train_test_split(
        df,
        test_size=0.20,                    # 80% train, 20% test
        stratify=df["trend_label"],        # equal classes in both
        random_state=42                    # reproducible split every time
    )

    print(f"\n[preprocess] Split:")
    print(f"  Total   : {len(df)} records")
    print(f"  Train   : {len(train_df)} records (80%)")
    print(f"  Test    : {len(test_df)} records (20%)")

    print(f"\n[preprocess] Train class distribution:")
    for trend, count in train_df["trend_label"].value_counts().items():
        print(f"  {trend:<45} {count}")

    print(f"\n[preprocess] Test class distribution:")
    for trend, count in test_df["trend_label"].value_counts().items():
        print(f"  {trend:<45} {count}")

    # ── Write JSONL files ─────────────────────────────────────────────────────
    write_jsonl(train_df, TRAIN_PATH)
    write_jsonl(test_df,  TEST_PATH)

    print(f"\n[preprocess] Saved:")
    print(f"  Train → {TRAIN_PATH}")
    print(f"  Test  → {TEST_PATH}")
    print(f"\n[preprocess] Done.")


if __name__ == "__main__":
    convert()