import os
import torch
import json
import re
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import PeftModel

MODEL_PATH = "/opt/ai-platform/models/gemma-2-2b-it"
ADAPTER_PATH = os.getenv("CTE_ADAPTER_PATH", "/opt/ai-platform/workspaces/aiuser9/cte/adapter")

SYSTEM_PROMPT = """You are a consumer trend analyst for an FMCG company in India.
Analyze retailer feedback and classify into EXACTLY ONE of these 15 trends:
rising_spicy_flavor_preference, youth_driven_consumption, fusion_flavor_adoption,
western_snack_influence, health_conscious_snacking, premium_packaging_demand,
regional_flavor_revival, convenience_format_preference, festive_gifting_trend,
online_impulse_buying, sugar_free_demand, protein_snack_trend,
small_pack_affordability_preference, plant_based_adoption, tangy_sour_flavor_rise
Respond ONLY with JSON: {"retailer_feedback": "...", "trend": "..."}"""

def load_model():
    print("Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(ADAPTER_PATH)
    print("Loading base model...")
    bnb_config = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.bfloat16)
    base_model = AutoModelForCausalLM.from_pretrained(MODEL_PATH, quantization_config=bnb_config, device_map="auto")
    print("Loading LoRA adapter...")
    model = PeftModel.from_pretrained(base_model, ADAPTER_PATH)
    model.eval()
    print("Model ready!")
    return model, tokenizer

def predict(feedback, model, tokenizer):
    prompt = f"<start_of_turn>user\n{SYSTEM_PROMPT}\n\nRetailer Feedback: {feedback}<end_of_turn>\n<start_of_turn>model\n"
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        outputs = model.generate(**inputs, max_new_tokens=100, do_sample=False, pad_token_id=tokenizer.eos_token_id)
    response = tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
    resp = response.strip()
    try:
        return json.loads(resp)
    except Exception:
        fixed = re.sub(r'("trend"\s*:\s*)([a-z_]+)', r'\1"\2"', resp)
        try:
            return json.loads(fixed)
        except Exception:
            match = re.search(r'"trend"\s*:\s*"?([a-z_]+)"?', resp)
            label = match.group(1) if match else resp
            return {"retailer_feedback": feedback, "trend": label}

if __name__ == "__main__":
    model, tokenizer = load_model()
    test_feedbacks = [
        "Kids are asking for spicy chips and hot sauce flavored snacks",
        "Customers requesting sugar-free biscuits and diet cookies",
        "Youth buying western style cheese puffs and nachos",
    ]
    for feedback in test_feedbacks:
        print(f"\nFeedback: {feedback}")
        result = predict(feedback, model, tokenizer)
        print(f"Result: {json.dumps(result, indent=2)}")


class TrendPredictor:
    def __init__(self):
        self.model, self.tokenizer = load_model()
    
    def predict(self, feedback):
        return predict(feedback, self.model, self.tokenizer)
