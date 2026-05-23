"""
model/evaluate.py
Standalone evaluation script.
Runs trained model against test split and reports accuracy.
Run anytime after training: python model/evaluate.py
"""
import sys
import json
import torch
import mlflow
from pathlib import Path
from collections import defaultdict

sys.path.append(str(Path(__file__).resolve().parent.parent))
from model.inference import TrendPredictor, VALID_TRENDS

ROOT      = Path(__file__).resolve().parent.parent
TEST_PATH = ROOT / "data" / "test.jsonl"
LOG_PATH  = ROOT / "data" / "evaluation_log.json"


def evaluate():
    if not TEST_PATH.exists():
        print(f"[evaluate] ERROR: test.jsonl not found at {TEST_PATH}")
        print(f"[evaluate] Run preprocess.py first to generate train/test splits.")
        return

    print(f"[evaluate] Loading test data from {TEST_PATH}")
    test_records = []
    with open(TEST_PATH, "r") as f:
        for line in f:
            test_records.append(json.loads(line))
    print(f"[evaluate] Test records: {len(test_records)}")

    print(f"[evaluate] Loading model...")
    predictor = TrendPredictor()

    correct        = 0
    total          = 0
    per_class      = defaultdict(lambda: {"correct": 0, "total": 0})
    wrong_examples = []
    all_results    = []

    print(f"[evaluate] Running predictions...")
    for i, sample in enumerate(test_records):
        messages   = sample["messages"]
        user_msg   = messages[1]["content"]
        true_trend = json.loads(messages[2]["content"])["trend"]

        # Extract feedback from user message
        feedback_line = [l for l in user_msg.split("\n") if l.startswith("Retailer Feedback:")]
        feedback = feedback_line[0].replace("Retailer Feedback:", "").strip() if feedback_line else user_msg[:100]

        result     = predictor.predict(feedback)
        predicted  = result["primary_trend"]
        confidence = result["primary_confidence"]
        is_correct = (predicted == true_trend)

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
    print(f"EVALUATION RESULTS")
    print(f"{'='*55}")
    print(f"Overall Accuracy : {accuracy}%  ({correct}/{total})")
    print(f"Wrong predictions: {len(wrong_examples)}")

    print(f"\nPer-class accuracy:")
    for trend in VALID_TRENDS:
        stats    = per_class[trend]
        cls_acc  = round(stats["correct"] / stats["total"] * 100, 1) if stats["total"] > 0 else 0
        bar      = "█" * int(cls_acc / 10) + "░" * (10 - int(cls_acc / 10))
        print(f"  {trend:<45} {bar} {cls_acc}% ({stats['correct']}/{stats['total']})")

    if wrong_examples:
        print(f"\nFirst 5 wrong predictions:")
        for ex in wrong_examples[:5]:
            print(f"  Record {ex['record']}: {ex['feedback'][:60]}...")
            print(f"    True:      {ex['true']}")
            print(f"    Predicted: {ex['predicted']} ({int(ex['confidence']*100)}% conf)")
            print()

    # ── Save log ───────────────────────────────────────────────────────────────
    log = {
        "accuracy":       accuracy,
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
        mlflow.set_experiment("consumer_trend_extraction")
        with mlflow.start_run(run_name="evaluation"):
            mlflow.log_metric("test_accuracy",    accuracy)
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