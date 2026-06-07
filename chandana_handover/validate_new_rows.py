"""
Validation script for new retailer feedback rows being added to dataset.csv

USAGE:
    python3 validate_new_rows.py <your_new_rows.csv>

Run this BEFORE sending your new rows back. It checks 14 realism rules
and prints PASS/FAIL for each.

Author: Afru, CTE intern, May 2026
"""
import pandas as pd
import sys
from pathlib import Path

TERRITORIES = {
    'Priya Sharma':    ['Hyderabad', 'Bangalore', 'Chennai'],
    'Deepa Nair':      ['Kochi', 'Coimbatore', 'Bangalore'],
    'Anjali Rao':      ['Hyderabad', 'Vizag', 'Chennai'],
    'Vikram Iyer':     ['Mumbai', 'Pune', 'Nagpur'],
    'Arjun Mehta':     ['Ahmedabad', 'Surat', 'Mumbai'],
    'Suresh Patel':    ['Ahmedabad', 'Surat', 'Pune'],
    'Meena Reddy':     ['Mumbai', 'Pune', 'Nagpur'],
    'Ravi Kumar':      ['Delhi', 'Chandigarh', 'Jaipur'],
    'Amit Singh':      ['Delhi', 'Lucknow', 'Chandigarh'],
    'Naresh Yadav':    ['Delhi', 'Jaipur', 'Lucknow'],
    'Rajesh Gupta':    ['Lucknow', 'Patna', 'Chandigarh'],
    'Sunita Verma':    ['Bhopal', 'Indore', 'Nagpur'],
    'Harish Babu':     ['Indore', 'Bhopal', 'Jaipur'],
    'Rekha Pillai':    ['Kolkata', 'Patna', 'Bhubaneswar'],
    'Kavita Joshi':    ['Kolkata', 'Bhubaneswar', 'Patna'],
}

LABEL_TO_SIGNAL = {
    'rising_spicy_flavor_preference': 'flavor_trend',
    'fusion_flavor_adoption':         'flavor_trend',
    'regional_flavor_revival':        'flavor_trend',
    'tangy_sour_flavor_rise':         'flavor_trend',
    'youth_driven_consumption':       'demographic_preference',
    'sugar_free_demand':              'demographic_preference',
    'protein_snack_trend':            'demographic_preference',
    'plant_based_adoption':           'demographic_preference',
    'health_conscious_snacking':      'buying_behavior_change',
    'convenience_format_preference':  'buying_behavior_change',
    'online_impulse_buying':          'buying_behavior_change',
    'western_snack_influence':        'buying_behavior_change',
    'festive_gifting_trend':          'seasonal_pattern',
    'premium_packaging_demand':       'seasonal_pattern',
    'small_pack_affordability_preference': 'demand_shift',
}

REQUIRED = ['record_id','visit_date','month','week_number','quarter','season',
            'city','store_type','retailer_id','salesperson_name',
            'consumer_demographic','product_category','retailer_feedback',
            'trend_signal_type','trend_label']

ALL_CITIES = sorted({c for cs in TERRITORIES.values() for c in cs})


def check(label, ok, fail_msg=""):
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    if not ok and fail_msg:
        print(f"         {fail_msg}")
    return ok


def validate(path):
    print(f"\n{'='*70}\nValidating: {path}\n{'='*70}")
    if not Path(path).exists():
        print(f"FILE NOT FOUND")
        return False

    df = pd.read_csv(path)
    issues = 0

    if not check("Has all 15 required columns",
                 all(c in df.columns for c in REQUIRED),
                 f"missing: {[c for c in REQUIRED if c not in df.columns]}"):
        issues += 1

    if not check("Zero null values", df.isnull().sum().sum() == 0,
                 f"nulls: {df.isnull().sum()[df.isnull().sum()>0].to_dict()}"):
        issues += 1

    bad_id = df[~df['record_id'].astype(str).str.match(r'^CTR-\d{4}$')]
    if not check("record_id format is CTR-XXXX", len(bad_id) == 0,
                 f"{len(bad_id)} bad ids"):
        issues += 1

    if not check("record_ids are unique", df['record_id'].duplicated().sum() == 0,
                 f"duplicates: {df[df['record_id'].duplicated()]['record_id'].tolist()[:5]}"):
        issues += 1

    bad_rep = df[~df['salesperson_name'].isin(TERRITORIES.keys())]
    if not check("Salesperson is one of 15 known reps", len(bad_rep) == 0,
                 f"unknown reps: {bad_rep['salesperson_name'].unique().tolist()}"):
        issues += 1

    bad_city = df[~df['city'].isin(ALL_CITIES)]
    if not check("City is one of 20 known cities", len(bad_city) == 0,
                 f"unknown cities: {bad_city['city'].unique().tolist()}"):
        issues += 1

    violations = []
    for _, r in df.iterrows():
        if r['salesperson_name'] in TERRITORIES and r['city'] not in TERRITORIES[r['salesperson_name']]:
            violations.append(r['record_id'])
    if not check("Salesperson stays in 3-city territory", len(violations) == 0,
                 f"{len(violations)} violations, first 3: {violations[:3]}"):
        issues += 1

    bad_trend = df[~df['trend_label'].isin(LABEL_TO_SIGNAL.keys())]
    if not check("trend_label is one of 15 known", len(bad_trend) == 0,
                 f"unknown: {bad_trend['trend_label'].unique().tolist()}"):
        issues += 1

    bad_map = []
    for _, r in df.iterrows():
        exp = LABEL_TO_SIGNAL.get(r['trend_label'])
        if exp and r['trend_signal_type'] != exp:
            bad_map.append(r['record_id'])
    if not check("trend_signal_type matches trend_label", len(bad_map) == 0,
                 f"{len(bad_map)} mismatches, first 3: {bad_map[:3]}"):
        issues += 1

    try:
        df['_vd'] = pd.to_datetime(df['visit_date'], errors='raise')
        check("visit_date is parseable", True)
    except Exception as e:
        check("visit_date is parseable", False, str(e))
        issues += 1
        return False

    if not check("month matches visit_date",
                 (df['month'] == df['_vd'].dt.month).all(),
                 f"{(df['month'] != df['_vd'].dt.month).sum()} mismatches"):
        issues += 1

    expected_q = 'Q' + ((df['_vd'].dt.month - 1) // 3 + 1).astype(str)
    if not check("quarter matches visit_date",
                 (df['quarter'] == expected_q).all(),
                 f"{(df['quarter'] != expected_q).sum()} mismatches"):
        issues += 1

    sd = df.groupby(['salesperson_name','_vd'])['city'].nunique()
    conflicts = sd[sd > 1]
    if not check("No same-day multi-city visits", len(conflicts) == 0,
                 f"{len(conflicts)} impossible conflicts"):
        issues += 1

    fl = df['retailer_feedback'].str.len()
    bad_len = ((fl < 30) | (fl > 250)).sum()
    if not check("Feedback length 30-250 chars", bad_len == 0,
                 f"{bad_len} rows out of range"):
        issues += 1

    print(f"\n{'='*70}")
    if issues == 0:
        print(f"OVERALL: PASS - {len(df)} rows ready to merge")
    else:
        print(f"OVERALL: FAIL - {issues} issue(s) above")
    print(f"{'='*70}")
    return issues == 0


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python3 validate_new_rows.py <file.csv>")
        sys.exit(1)
    sys.exit(0 if validate(sys.argv[1]) else 1)
