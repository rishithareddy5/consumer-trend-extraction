"""
model/evaluate.py
Standalone evaluation script.
Runs trained model against test split and reports accuracy.
Run anytime after training: python model/evaluate.py
"""
import sys
import json
import torch
try:
    import mlflow
except ImportError:
    mlflow = None
from pathlib import Path
from collections import defaultdict

sys.path.append(str(Path(__file__).resolve().parent.parent))
from model.inference import TrendPredictor

VALID_TRENDS = [
    "rising_spicy_flavor_preference", "youth_driven_consumption",
    "fusion_flavor_adoption", "western_snack_influence",
    "health_conscious_snacking", "premium_packaging_demand",
    "regional_flavor_revival", "convenience_format_preference",
    "festive_gifting_trend", "online_impulse_buying",
    "sugar_free_demand", "protein_snack_trend",
    "small_pack_affordability_preference", "plant_based_adoption",
    "tangy_sour_flavor_rise",
]

ROOT      = Path(__file__).resolve().parent.parent
TEST_PATH = ROOT / "data" / "test.jsonl"
LOG_PATH  = ROOT / "data" / "evaluation_log.json"


def extract_feedback(user_msg: str) -> str:
    """Extract retailer feedback text from the user message."""
    feedback_line = [l for l in user_msg.split("\n") if l.startswith("Retailer Feedback:")]
    if feedback_line:
        return feedback_line[0].replace("Retailer Feedback:", "").strip()
    return user_msg[:100]


def load_test_records() -> list:
    """Load test records from test.jsonl."""
    records = []
    with open(TEST_PATH, "r") as f:
        for line in f:
            records.append(json.loads(line))
    return records


def evaluate():
    if not TEST_PATH.exists():
        print(f"[evaluate] ERROR: test.jsonl not found at {TEST_PATH}")
        print("[evaluate] Run preprocess.py first to generate train/test splits.")
        return

    print(f"[evaluate] Loading test data from {TEST_PATH}")
    test_records = []
    with open(TEST_PATH, "r") as f:
        for line in f:
            test_records.append(json.loads(line))
    print(f"[evaluate] Test records: {len(test_records)}")

    print("[evaluate] Loading model...")
    predictor = TrendPredictor()

    correct        = 0
    total          = 0
    per_class      = defaultdict(lambda: {"correct": 0, "total": 0})
    wrong_examples = []
    all_results    = []

    correct_top2 = 0
    print("[evaluate] Running predictions...")
    for i, sample in enumerate(test_records):
        messages   = sample["messages"]
        user_msg   = messages[1]["content"]
        true_trend = json.loads(messages[2]["content"])["trend"]

        feedback = extract_feedback(user_msg)

        result     = predictor.predict(feedback)
        _raw = result.get("primary_trend") or result.get("trend", "unknown")
        if isinstance(_raw, str) and _raw.strip().startswith("{"):
            try:
                _raw = json.loads(_raw).get("trend", _raw)
            except Exception:
                pass
        predicted = _raw
        secondary = result.get("secondary_trend", "")
        confidence = result.get("primary_confidence", 1.0)
        is_correct = (predicted == true_trend)
        is_correct_top2 = is_correct or (secondary == true_trend)
        if is_correct_top2:
            correct_top2 += 1

        if is_correct:
            correct += 1
        else:
            wrong_examples.append({
                "record":    i + 1,
                "feedback":  feedback[:80],
                "true":      true_trend,
                "predicted": predicted,
                "confidence": confidence,
            })

        per_class[true_trend]["total"]   += 1
        if is_correct:
            per_class[true_trend]["correct"] += 1
        total += 1

        all_results.append({
            "feedback":   feedback[:80],
            "true":       true_trend,
            "predicted":  predicted,
            "confidence": confidence,
            "correct":    is_correct,
        })

        if (i + 1) % 10 == 0:
            print(f"  Processed {i+1}/{total} — running accuracy: {round(correct/(i+1)*100,1)}%")

    # ── Final results ──────────────────────────────────────────────────────────
    accuracy = round(correct / total * 100, 2) if total > 0 else 0

    print(f"\n{'='*55}")
    print("EVALUATION RESULTS")
    print(f"{'='*55}")
    accuracy_top2 = round(correct_top2 / total * 100, 2) if total > 0 else 0
    print(f"Overall Accuracy : {accuracy}%  ({correct}/{total})")
    print(f"Top-2 Accuracy   : {accuracy_top2}%  ({correct_top2}/{total})")
    print(f"Wrong predictions: {len(wrong_examples)}")

    print("\nPer-class accuracy:")
    for trend in VALID_TRENDS:
        stats    = per_class[trend]
        cls_acc  = round(stats["correct"] / stats["total"] * 100, 1) if stats["total"] > 0 else 0
        bar      = "█" * int(cls_acc / 10) + "░" * (10 - int(cls_acc / 10))
        print(f"  {trend:<45} {bar} {cls_acc}% ({stats['correct']}/{stats['total']})")

    if wrong_examples:
        print("\nFirst 5 wrong predictions:")
        for ex in wrong_examples[:5]:
            print(f"  Record {ex['record']}: {ex['feedback'][:60]}...")
            print(f"    True:      {ex['true']}")
            print(f"    Predicted: {ex['predicted']} ({int(ex['confidence']*100)}% conf)")
            print()

    # ── Save log ───────────────────────────────────────────────────────────────
    log = {
        "accuracy":       accuracy,
        "accuracy_top2":  accuracy_top2,
        "correct":        correct,
        "total":          total,
        "per_class":      {k: v for k, v in per_class.items()},
        "wrong_examples": wrong_examples,
        "all_results":    all_results,
    }
    with open(LOG_PATH, "w") as f:
        json.dump(log, f, indent=2)
    print(f"\nDetailed log saved → {LOG_PATH}")

    # ── Log to MLflow ──────────────────────────────────────────────────────────
    try:
        if mlflow is not None:
            mlflow.set_experiment("consumer_trend_extraction")
            with mlflow.start_run(run_name="evaluation"):
                mlflow.log_metric("test_accuracy",    accuracy)
                mlflow.log_metric("test_accuracy_top2", accuracy_top2)
                mlflow.log_metric("correct",          correct)
                mlflow.log_metric("total",            total)
                mlflow.log_metric("wrong_predictions",len(wrong_examples))
                mlflow.log_artifact(str(LOG_PATH))
        print("Results logged to MLflow.")
    except Exception as e:
        print(f"MLflow logging skipped: {e}")

    print(f"\n{'='*55}")
    if accuracy >= 80:
        print(f"RESULT: GOOD — {accuracy}% accuracy. Model is reliable.")
    elif accuracy >= 65:
        print(f"RESULT: ACCEPTABLE — {accuracy}%. Add more training data.")
    else:
        print(f"RESULT: NEEDS IMPROVEMENT — {accuracy}%. Review dataset quality.")
    print(f"{'='*55}\n")

    return log


if __name__ == "__main__":
    evaluate()