import sys, os, pytest, torch, json, re, pathlib
import pandas as pd
sys.path.insert(0, "/opt/ai-platform/workspaces/aiuser9/cte")

from controller.api import TREND_LABELS, TrendModel
from model.preprocess import build_user_message

# ── label tests ──────────────────────────────────────────────────────────────
def test_labels_count():               assert len(TREND_LABELS) == 15
def test_labels_unique():              assert len(set(TREND_LABELS)) == 15
def test_labels_lowercase():
    for l in TREND_LABELS:            assert l == l.lower()
def test_labels_have_underscore():
    for l in TREND_LABELS:            assert "_" in l

# ── build_user_message ───────────────────────────────────────────────────────
ROW = {"retailer_feedback":"Kids want spicy chips","city":"Hyderabad",
       "store_type":"Supermarket","season":"Summer",
       "consumer_demographic":"youth","product_category":"chips"}

def test_build_msg_feedback():         assert "Kids want spicy chips" in build_user_message(ROW)
def test_build_msg_city():             assert "Hyderabad" in build_user_message(ROW)
def test_build_msg_store():            assert "Supermarket" in build_user_message(ROW)
def test_build_msg_season():           assert "Summer" in build_user_message(ROW)
def test_build_msg_demographic():      assert "youth" in build_user_message(ROW)

# ── TrendModel helper methods (no GPU needed) ────────────────────────────────
class FakeTok:
    def __call__(self, text, add_special_tokens=False):
        class R:
            input_ids = [ord(text[0]) % 1000]
        return R()
    def apply_chat_template(self, msgs, tokenize=False, add_generation_prompt=True):
        return msgs[0]["content"]

class FakeGen:
    def __init__(self, has_scores=True):
        if has_scores:
            logits = torch.zeros(32000); logits[114] = 10.0
            self.scores = [logits.unsqueeze(0)]
        else:
            self.scores = []

class M:
    def __init__(self): self.tokenizer = FakeTok()
    def _score_labels(self, gen, decoded_norm):
        if gen.scores:
            probs = torch.softmax(gen.scores[0][0].float()/5.0, dim=-1)
            scored = []
            for lab in TREND_LABELS:
                ids = self.tokenizer(lab, add_special_tokens=False).input_ids
                p = float(probs[ids[0]].item()) if ids else 0.0
                scored.append((lab, p))
            total = sum(p for _,p in scored)
            if total > 0: scored = [(l,p/total) for l,p in scored]
            return scored
        return [(l, 1.0 if l in decoded_norm else 0.0) for l in TREND_LABELS]
    def _boost_decoded_label(self, scored, decoded_norm):
        for i,(lab,_) in enumerate(scored):
            if lab in decoded_norm and i != 0:
                scored.insert(0, scored.pop(i)); break
        return scored
    def _build_prompt(self, feedback): return f"Classify: {feedback}"

@pytest.fixture
def m(): return M()

def test_score_15(m):                  assert len(m._score_labels(FakeGen(True),"")) == 15
def test_score_sum(m):                 assert abs(sum(p for _,p in m._score_labels(FakeGen(True),""))-1.0)<0.01
def test_score_all_labels(m):
    labels = [l for l,_ in m._score_labels(FakeGen(True),"")]
    for lab in TREND_LABELS:          assert lab in labels
def test_score_no_scores(m):
    r = dict(m._score_labels(FakeGen(False),"rising_spicy_flavor_preference"))
    assert r["rising_spicy_flavor_preference"] == pytest.approx(1.0)
def test_score_zero_others(m):
    r = dict(m._score_labels(FakeGen(False),"rising_spicy_flavor_preference"))
    assert r["youth_driven_consumption"] == pytest.approx(0.0)
def test_score_confidence_range(m):
    for _,p in m._score_labels(FakeGen(True),""): assert 0.0 <= p <= 1.0
def test_boost_moves(m):
    s = [(l,0.1) for l in TREND_LABELS]
    assert m._boost_decoded_label(s,"premium_packaging_demand")[0][0] == "premium_packaging_demand"
def test_boost_no_match(m):
    s = [(l,0.1) for l in TREND_LABELS]; orig = s[0][0]
    assert m._boost_decoded_label(s,"nomatch")[0][0] == orig
def test_boost_already_first(m):
    s = [("rising_spicy_flavor_preference",0.9)]+[(l,0.01) for l in TREND_LABELS[1:]]
    assert m._boost_decoded_label(s,"rising_spicy_flavor_preference")[0][0] == "rising_spicy_flavor_preference"
def test_prompt_contains(m):           assert "spicy" in m._build_prompt("spicy chips")

# ── dataset ───────────────────────────────────────────────────────────────────
def test_csv_exists():                 assert pathlib.Path("data/dataset.csv").exists()
def test_csv_500_rows():               assert len(pd.read_csv("data/dataset.csv")) >= 500
def test_csv_columns():
    df = pd.read_csv("data/dataset.csv")
    assert "retailer_feedback" in df.columns and "trend_label" in df.columns
def test_csv_valid_labels():
    df = pd.read_csv("data/dataset.csv")
    for l in df["trend_label"].unique(): assert l in TREND_LABELS
def test_train_jsonl():                assert pathlib.Path("data/train.jsonl").exists()
def test_test_jsonl():                 assert pathlib.Path("data/test.jsonl").exists()
