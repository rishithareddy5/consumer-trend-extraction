"""
model/validate.py
Standalone dataset validation script.
Checks quality before training — nulls, duplicates,
class balance, season correctness.
Run: python model/validate.py
"""
import sys
import pandas as pd
from pathlib import Path

ROOT       = Path(__file__).resolve().parent.parent
EXCEL_PATH = ROOT / "data" / "Consumer_Trend_Extraction_Dataset.xlsx"

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

SEASON_MONTH_MAP = {
    "Winter":       [12, 1, 2],
    "Summer":       [3, 4, 5, 6],
    "Monsoon":      [7, 8, 9],
    "Post-Festive": [11, 12],
    "Festive":      [10, 11],
    "Diwali":       [10, 11],
    "Holi":         [2, 3],
    "Onam":         [8, 9],
    "Ramadan":      [3, 4],
    "New Year":     [12, 1],
}

REQUIRED_COLS = [
    "record_id","visit_date","season","city","store_type",
    "salesperson_name","consumer_demographic","product_category",
    "retailer_feedback","trend_signal_type","trend_label","structured_json",
]


def validate():
    print(f"\n[validate] Reading: {EXCEL_PATH}")
    df = pd.read_excel(EXCEL_PATH, sheet_name="Training_Dataset")
    df["visit_date"] = pd.to_datetime(df["visit_date"])

    issues  = []
    passed  = []

    # 1. Row count
    if len(df) >= 500:
        passed.append(f"Row count: {len(df)} records (minimum 500 met)")
    else:
        issues.append(f"Row count: {len(df)} — below minimum 500")

    # 2. Required columns
    missing_cols = [c for c in REQUIRED_COLS if c not in df.columns]
    if not missing_cols:
        passed.append(f"All {len(REQUIRED_COLS)} required columns present")
    else:
        issues.append(f"Missing columns: {missing_cols}")

    # 3. Null values
    nulls = df.isnull().sum()
    null_cols = nulls[nulls > 0]
    if null_cols.empty:
        passed.append("No null values in any column")
    else:
        issues.append(f"Null values found: {null_cols.to_dict()}")

    # 4. Duplicate feedbacks
    dupes = df.duplicated("retailer_feedback").sum()
    if dupes == 0:
        passed.append("No duplicate retailer feedbacks")
    else:
        issues.append(f"{dupes} duplicate retailer feedbacks found")

    # 5. Invalid trend labels
    invalid = df[~df["trend_label"].isin(VALID_TRENDS)]["trend_label"].unique()
    if len(invalid) == 0:
        passed.append(f"All trend labels valid — {df['trend_label'].nunique()} unique classes")
    else:
        issues.append(f"Invalid trend labels: {invalid}")

    # 6. Class balance
    counts   = df["trend_label"].value_counts()
    min_count = counts.min()
    max_count = counts.max()
    imbalance = round((max_count - min_count) / max_count * 100, 1)
    if imbalance <= 20:
        passed.append(f"Class balance good — min:{min_count} max:{max_count} imbalance:{imbalance}%")
    else:
        issues.append(f"Class imbalance: {imbalance}% — min:{min_count} max:{max_count}")

    # 7. Season-date mismatches
    bad_seasons = 0
    for _, row in df.iterrows():
        month        = row["visit_date"].month
        season       = row["season"]
        valid_months = SEASON_MONTH_MAP.get(season, [])
        if valid_months and month not in valid_months:
            bad_seasons += 1
    if bad_seasons == 0:
        passed.append("All season-date mappings correct")
    else:
        issues.append(f"{bad_seasons} season-date mismatches found")

    # 8. Date range
    min_date = df["visit_date"].min().strftime("%Y-%m-%d")
    max_date = df["visit_date"].max().strftime("%Y-%m-%d")
    passed.append(f"Date range: {min_date} to {max_date}")

    # ── Print report ───────────────────────────────────────────────────────────
    print(f"\n{'='*55}")
    print(f"DATASET VALIDATION REPORT")
    print(f"{'='*55}")

    print(f"\nPASSED ({len(passed)}):")
    for p in passed:
        print(f"  ✅ {p}")

    if issues:
        print(f"\nISSUES ({len(issues)}):")
        for issue in issues:
            print(f"  ❌ {issue}")
    else:
        print(f"\nNo issues found.")

    print(f"\nClass distribution:")
    for trend, count in df["trend_label"].value_counts().items():
        bar = "█" * count + "░" * (max_count - count)
        print(f"  {trend:<45} {count:>3}")

    print(f"\n{'='*55}")
    if not issues:
        print("RESULT: Dataset is ready for training.")
    else:
        print(f"RESULT: Fix {len(issues)} issue(s) before training.")
    print(f"{'='*55}\n")

    return len(issues) == 0


if __name__ == "__main__":
    ok = validate()
    sys.exit(0 if ok else 1)