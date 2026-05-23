"""
model/train.py
Fine-tunes Gemma 2B with 4-bit QLoRA (PEFT + LoRA + BitsAndBytes).
Tracks experiment with MLflow.
Run: python model/train.py
"""
import torch
import mlflow
from pathlib import Path
from datasets import load_dataset
from transformers import (
    AutoTokenizer, AutoModelForCausalLM,
    BitsAndBytesConfig, TrainingArguments,
)
from peft import LoraConfig, get_peft_model, TaskType
from trl import SFTTrainer

ROOT       = Path(__file__).resolve().parent.parent
DATA_PATH  = ROOT / "data" / "batch1_500.jsonl"
OUTPUT_DIR = ROOT / "adapter"
MODEL_ID   = "google/gemma-2b-it"

# ── 4-bit QLoRA config ────────────────────────────────────────────────────────
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
)

# ── LoRA config (PEFT) ────────────────────────────────────────────────────────
lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type=TaskType.CAUSAL_LM,
)


def format_sample(sample):
    """Convert chat messages to Gemma instruction format."""
    text = ""
    for msg in sample["messages"]:
        if msg["role"] == "system":
            text += f"<start_of_turn>system\n{msg['content']}<end_of_turn>\n"
        elif msg["role"] == "user":
            text += f"<start_of_turn>user\n{msg['content']}<end_of_turn>\n"
        elif msg["role"] == "assistant":
            text += f"<start_of_turn>model\n{msg['content']}<end_of_turn>\n"
    return {"text": text}


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

    print(f"[train] Loading dataset: {DATA_PATH}")
    dataset = load_dataset("json", data_files=str(DATA_PATH), split="train")
    dataset = dataset.map(format_sample)
    print(f"[train] Dataset: {len(dataset)} records")

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
        train_dataset=dataset,
        tokenizer=tokenizer,
        dataset_text_field="text",
        max_seq_length=1024,
        packing=False,
    )

    # ── MLflow tracking ───────────────────────────────────────────────────────
    mlflow.set_experiment("consumer_trend_extraction")
    with mlflow.start_run(run_name="gemma2b_qlora_batch1"):
        mlflow.log_params({
            "model": MODEL_ID, "lora_r": 16, "lora_alpha": 32,
            "epochs": 3, "batch_size": 2, "learning_rate": 2e-4,
            "training_samples": len(dataset),
        })
        print("[train] Fine-tuning started...")
        trainer.train()
        final_loss = trainer.state.log_history[-1].get("loss", 0)
        mlflow.log_metric("final_train_loss", final_loss)
        print(f"[train] Final loss: {final_loss:.4f}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(str(OUTPUT_DIR))
    tokenizer.save_pretrained(str(OUTPUT_DIR))
    print(f"[train] Adapter saved → {OUTPUT_DIR}")


if __name__ == "__main__":
    train()
