import torch
import logging
from pathlib import Path
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, BitsAndBytesConfig
from peft import LoraConfig, get_peft_model, TaskType
from trl import SFTTrainer

ROOT = Path(__file__).resolve().parent.parent
TRAIN_PATH = ROOT / "data" / "train.jsonl"
OUTPUT_DIR = ROOT / "adapter"
LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

MODEL_PATH = "/opt/ai-platform/models/gemma-2-2b-it"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [train] %(message)s",
    handlers=[logging.FileHandler(str(LOG_DIR / "train.log")), logging.StreamHandler()])
log = logging.getLogger(__name__)

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
)

lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type=TaskType.CAUSAL_LM
)

def format_sample(sample):
    text = ""
    system_content = ""
    for msg in sample["messages"]:
        if msg["role"] == "system":
            system_content = msg["content"]
        elif msg["role"] == "user":
            combined = f"{system_content}\n\n{msg['content']}" if system_content else msg["content"]
            text += f"<start_of_turn>user\n{combined}<end_of_turn>\n"
        elif msg["role"] == "assistant":
            text += f"<start_of_turn>model\n{msg['content']}<end_of_turn>\n"
    return {"text": text}

def train():
    log.info("Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    tokenizer.pad_token = tokenizer.eos_token
    log.info("Tokenizer loaded.")

    log.info("Loading model with 4-bit QLoRA...")
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_PATH,
        quantization_config=bnb_config,
        device_map="auto"
    )
    model.config.use_cache = False
    log.info("Model loaded.")

    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    dataset = load_dataset("json", data_files=str(TRAIN_PATH), split="train")
    dataset = dataset.map(format_sample)
    log.info(f"Training records: {len(dataset)}")

    training_args = TrainingArguments(
        output_dir=str(OUTPUT_DIR),
        num_train_epochs=3,
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        learning_rate=2e-4,
        bf16=True,
        logging_steps=10,
        save_strategy="epoch",
        report_to="none",
    )

    trainer = SFTTrainer(
        model=model,
        args=training_args,
        train_dataset=dataset.select_columns(["text"]),
        processing_class=tokenizer,
    )

    log.info("Starting fine-tuning...")
    trainer.train()

    final_loss = trainer.state.log_history[-1].get("loss", 0)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(str(OUTPUT_DIR))
    tokenizer.save_pretrained(str(OUTPUT_DIR))
    log.info(f"Training complete! Loss: {final_loss:.4f}")
    print(f"\nTRAINING COMPLETE — Loss: {final_loss:.4f}")

if __name__ == "__main__":
    train()
