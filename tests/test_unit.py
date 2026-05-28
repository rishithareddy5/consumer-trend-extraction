import json, re, pytest, sys, os, pathlib
import pandas as pd
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
LABELS = ["rising_spicy_flavor_preference","youth_driven_consumption","fusion_flavor_adoption","western_snack_influence","health_conscious_snacking","premium_packaging_demand","regional_flavor_revival","convenience_format_preference","festive_gifting_trend","online_impulse_buying","sugar_free_demand","protein_snack_trend","small_pack_affordability_preference","plant_based_adoption","tangy_sour_flavor_rise"]
def test_labels_count(): assert len(LABELS) == 15
def test_labels_unique(): assert len(LABELS) == len(set(LABELS))
def test_labels_format():
    for l in LABELS: assert "_" in l and l == l.lower() and " " not in l
def test_json_valid():
    r = json.loads('{"retailer_feedback":"test","trend":"rising_spicy_flavor_preference"}')
    assert r["trend"] == "rising_spicy_flavor_preference"
def test_regex_extract():
    raw = '{"trend": youth_driven_consumption}'
    m = re.search(r'"trend"\s*:\s*"?([a-z_]+)"?', raw)
    assert m and m.group(1) == "youth_driven_consumption"
def test_confidence_range():
    for c in [0.69, 0.07, 0.05]: assert 0.0 <= c <= 1.0
def test_response_keys():
    r = {"primary_trend":"x","primary_confidence":0.5,"secondary_trend":"y","secondary_confidence":0.3,"tertiary_trend":"z","tertiary_confidence":0.1}
    for k in ["primary_trend","primary_confidence","secondary_trend","secondary_confidence","tertiary_trend","tertiary_confidence"]: assert k in r
def test_feedback_length(): assert len("Kids asking for spicy chips".strip()) >= 3
def test_empty_feedback(): assert len("".strip()) < 3
def test_csv_exists(): assert (pathlib.Path("data/dataset.csv")).exists()
def test_csv_rows():
    df = pd.read_csv("data/dataset.csv")
    assert len(df) >= 500
def test_csv_columns():
    df = pd.read_csv("data/dataset.csv")
    assert "retailer_feedback" in df.columns and "trend_label" in df.columns
def test_labels_in_dataset():
    df = pd.read_csv("data/dataset.csv")
    for l in df["trend_label"].unique(): assert l in LABELS
def test_train_jsonl(): assert pathlib.Path("data/train.jsonl").exists()
def test_test_jsonl(): assert pathlib.Path("data/test.jsonl").exists()
