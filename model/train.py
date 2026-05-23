"""
model/train.py
Fine-tunes Gemma 2B with 4-bit QLoRA on train split only.
Evaluates on test split after training.
Tracks everything with MLflow.
Run: python model/train.py
"""
import json
import torch
import mlflow
import pandas as pd
from pathlib import Path
from datasets import load_dataset
from transformers import (
    AutoTokenizer, AutoModelForCausalLM,
    BitsAndBytesConfig, TrainingArguments,
)
from peft import LoraConfig, get_peft_model, TaskType
from trl import SFTTrainer

ROOT       = Path(__file__).resolve().parent.parent
TRAIN_PATH = ROOT / "data" / "train.jsonl"
TEST_PATH  = ROOT / "data" / "test.jsonl"
OUTPUT_DIR = ROOT / "adapter"
MODEL_ID   = "google/gemma-2b-it"

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

# ── 4-bit QLoRA ───────────────────────────────────────────────────────────────
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
)

# ── LoRA ──────────────────────────────────────────────────────────────────────
lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type=TaskType.CAUSAL_LM,
)


def format_sample(sample):
    text = ""
    for msg in sample["messages"]:
        if msg["role"] == "system":
            text += f"<start_of_turn>system\n{msg['content']}<end_of_turn>\n"
        elif msg["role"] == "user":
            text += f"<start_of_turn>user\n{msg['content']}<end_of_turn>\n"
        elif msg["role"] == "assistant":
            text += f"<start_of_turn>model\n{msg['content']}<end_of_turn>\n"
    return {"text": text}


def evaluate_on_test(model, tokenizer, test_path: Path) -> dict:
    """
    Evaluate trained model on test split.
    Returns accuracy, per-class accuracy, and confusion details.
    Test split was NEVER seen during training — honest evaluation.
    """
    print("\n[train] Evaluating on test split...")
    test_data = []
    with open(test_path, "r") as f:
        for line in f:
            test_data.append(json.loads(line))

    correct   = 0
    total     = 0
    per_class = {t: {"correct": 0, "total": 0} for t in VALID_TRENDS}
    wrong_examples = []

    model.eval()
    for sample in test_data:
        messages  = sample["messages"]
        user_msg  = messages[1]["content"]
        true_trend = json.loads(messages[2]["content"])["trend"]

        prompt = (
            f"<start_of_turn>system\n{messages[0]['content']}<end_of_turn>\n"
            f"<start_of_turn>user\n{user_msg}<end_of_turn>\n"
            f"<start_of_turn>model\n"
        )

        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=100,
                temperature=0.05,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id,
            )
        response = tokenizer.decode(
            outputs[0][inputs["input_ids"].shape[1]:],
            skip_special_tokens=True
        ).strip()

        # Parse predicted trend
        predicted = None
        try:
            clean = response.replace("```json","").replace("```","").strip()
            parsed = json.loads(clean)
            if parsed.get("trend") in VALID_TRENDS:
                predicted = parsed["trend"]
        except:
            for t in VALID_TRENDS:
                if t in response:
                    predicted = t
                    break

        if predicted is None:
            predicted = "unknown"

        # Track accuracy
        is_correct = (predicted == true_trend)
        if is_correct:
            correct += 1
        else:
            wrong_examples.append({
                "true":      true_trend,
                "predicted": predicted,
            })

        per_class[true_trend]["total"]   += 1
        if is_correct:
            per_class[true_trend]["correct"] += 1
        total += 1

    accuracy = round(correct / total * 100, 2) if total > 0 else 0

    print(f"\n[train] Test Results:")
    print(f"  Overall Accuracy: {accuracy}% ({correct}/{total})")
    print(f"\n  Per-class accuracy:")
    for trend, stats in per_class.items():
        if stats["total"] > 0:
            cls_acc = round(stats["correct"] / stats["total"] * 100, 1)
            print(f"    {trend:<45} {cls_acc}% ({stats['correct']}/{stats['total']})")

    if wrong_examples:
        print(f"\n  Wrong predictions (first 5):")
        for ex in wrong_examples[:5]:
            print(f"    True: {ex['true']}")
            print(f"    Pred: {ex['predicted']}")
            print()

    return {
        "test_accuracy":    accuracy,
        "correct":          correct,
        "total":            total,
        "per_class":        per_class,
        "wrong_examples":   wrong_examples,
    }


def train():
    print(f"[train] Loading base model: {MODEL_ID}")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
    )
    model.config.use_cache = False

    print("[train] Attaching LoRA adapter...")
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    # ── Load TRAIN split only ─────────────────────────────────────────────────
    print(f"[train] Loading training data: {TRAIN_PATH}")
    train_dataset = load_dataset(
        "json", data_files=str(TRAIN_PATH), split="train"
    )
    train_dataset = train_dataset.map(format_sample)
    print(f"[train] Training records: {len(train_dataset)}")
    print(f"[train] Test split will be used for evaluation AFTER training")

    training_args = TrainingArguments(
        output_dir=str(OUTPUT_DIR),
        num_train_epochs=3,
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        learning_rate=2e-4,
        lr_scheduler_type="cosine",
        warmup_ratio=0.05,
        bf16=True,
        fp16=False,
        logging_steps=10,
        save_strategy="epoch",
        report_to="none",
    )

    trainer = SFTTrainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        tokenizer=tokenizer,
        dataset_text_field="text",
        max_seq_length=1024,
        packing=False,
    )

    # ── MLflow tracking ───────────────────────────────────────────────────────
    mlflow.set_experiment("consumer_trend_extraction")
    with mlflow.start_run(run_name="gemma2b_qlora_batch1"):
        mlflow.log_params({
            "model":            MODEL_ID,
            "lora_r":           16,
            "lora_alpha":       32,
            "epochs":           3,
            "batch_size":       2,
            "learning_rate":    2e-4,
            "train_samples":    len(train_dataset),
            "test_samples":     sum(1 for _ in open(TEST_PATH)),
            "train_test_split": "80/20 stratified",
        })

        print("[train] Fine-tuning started...")
        trainer.train()

        final_loss = trainer.state.log_history[-1].get("loss", 0)
        mlflow.log_metric("final_train_loss", final_loss)
        print(f"[train] Final training loss: {final_loss:.4f}")

        # ── Evaluate on test split ────────────────────────────────────────────
        eval_results = evaluate_on_test(model, tokenizer, TEST_PATH)

        mlflow.log_metric("test_accuracy",    eval_results["test_accuracy"])
        mlflow.log_metric("test_correct",     eval_results["correct"])
        mlflow.log_metric("test_total",       eval_results["total"])

        print(f"\n[train] Final test accuracy: {eval_results['test_accuracy']}%")

    # ── Save adapter ──────────────────────────────────────────────────────────
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(str(OUTPUT_DIR))
    tokenizer.save_pretrained(str(OUTPUT_DIR))
    print(f"[train] Adapter saved → {OUTPUT_DIR}")

    return eval_results


if __name__ == "__main__":
    results = train()
    print(f"\n{'='*50}")
    print(f"TRAINING COMPLETE")
    print(f"Test Accuracy: {results['test_accuracy']}%")
    print(f"{'='*50}")