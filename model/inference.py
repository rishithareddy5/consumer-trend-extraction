"""
model/inference.py
Loads Gemma 2B + LoRA adapter. Returns top-3 trends with confidence scores.
Speaker said: "show at least 3 categories with confidence ranking"
"""
import json
import torch
import numpy as np
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import PeftModel

ROOT     = Path(__file__).resolve().parent.parent
ADAPTER  = ROOT / "adapter"
MODEL_ID = "google/gemma-2b-it"

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

SYSTEM_PROMPT = """You are a consumer trend analyst for an FMCG company in India.
Analyze retailer feedback from field salespersons and classify the dominant consumer
trend into EXACTLY ONE of these 15 labels:

rising_spicy_flavor_preference | youth_driven_consumption | fusion_flavor_adoption
western_snack_influence | health_conscious_snacking | premium_packaging_demand
regional_flavor_revival | convenience_format_preference | festive_gifting_trend
online_impulse_buying | sugar_free_demand | protein_snack_trend
small_pack_affordability_preference | plant_based_adoption | tangy_sour_flavor_rise

Rules:
- Output ONLY valid JSON. No explanation, no extra text.
- Format: {"retailer_feedback": "...", "trend": "..."}
- trend MUST be exactly one label. Never invent new labels."""


class TrendPredictor:
    """
    Loads fine-tuned Gemma 2B + LoRA adapter.
    Produces top-3 trend labels with confidence scores (speaker's requirement).
    """

    def __init__(self):
        print("[inference] Loading model...")
        bnb = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16,
        )
        self.tokenizer = AutoTokenizer.from_pretrained(str(ADAPTER))
        self.tokenizer.pad_token = self.tokenizer.eos_token

        base = AutoModelForCausalLM.from_pretrained(
            MODEL_ID,
            quantization_config=bnb,
            device_map="auto",
            trust_remote_code=True,
        )
        self.model = PeftModel.from_pretrained(base, str(ADAPTER))
        self.model.eval()
        print("[inference] Model ready.")

    def _build_prompt(self, feedback, city="", store_type="",
                      demographic="", season="", context_examples=None):
        context = ""
        if context_examples:
            context = "\nSimilar past observations:\n"
            for i, ex in enumerate(context_examples, 1):
                context += f"  {i}. {ex['feedback']} → {ex['trend']}\n"

        user = f"""Analyze this retailer feedback and identify the primary consumer trend.

Retailer Feedback: {feedback}
City: {city} | Store Type: {store_type}
Season: {season} | Consumer Demographic: {demographic}
{context}
Respond ONLY with JSON: {{"retailer_feedback": "...", "trend": "..."}}"""

        return (
            f"<start_of_turn>system\n{SYSTEM_PROMPT}<end_of_turn>\n"
            f"<start_of_turn>user\n{user}<end_of_turn>\n"
            f"<start_of_turn>model\n"
        )

    def _get_confidence_scores(self, prompt):
        """
        Compute probability for each of the 15 trend labels.
        This gives the confidence scores the speaker asked for.
        """
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        with torch.no_grad():
            logits = self.model(**inputs).logits[0, -1, :]

        scores = {}
        for trend in VALID_TRENDS:
            tokens = self.tokenizer.encode(trend, add_special_tokens=False)
            if tokens:
                scores[trend] = logits[tokens[0]].item()

        # Softmax → probabilities
        vals = np.array(list(scores.values()))
        probs = np.exp(vals - vals.max()) / np.exp(vals - vals.max()).sum()
        return {t: round(float(p), 4) for t, p in zip(scores.keys(), probs)}

    def _generate(self, prompt):
        """Generate structured JSON output."""
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        with torch.no_grad():
            out = self.model.generate(
                **inputs,
                max_new_tokens=200,
                temperature=0.05,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
            )
        return self.tokenizer.decode(
            out[0][inputs["input_ids"].shape[1]:],
            skip_special_tokens=True
        ).strip()

    def predict(self, feedback, city="", store_type="",
                demographic="", season="", context_examples=None):
        """
        Returns top-3 trends with confidence scores.
        Speaker: "at least 3 categories you should show the confidence"
        """
        prompt = self._build_prompt(
            feedback, city, store_type, demographic, season, context_examples
        )

        # Get confidence scores across all 15 trends
        scores = self._get_confidence_scores(prompt)
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        # Validate generated JSON output
        raw = self._generate(prompt)
        primary = ranked[0][0]
        try:
            parsed = json.loads(raw)
            if parsed.get("trend") in VALID_TRENDS:
                primary = parsed["trend"]
        except (json.JSONDecodeError, KeyError):
            pass  # fallback to confidence-based top trend

        return {
            "retailer_feedback":    feedback,
            "primary_trend":        ranked[0][0],
            "primary_confidence":   ranked[0][1],
            "secondary_trend":      ranked[1][0],
            "secondary_confidence": ranked[1][1],
            "tertiary_trend":       ranked[2][0],
            "tertiary_confidence":  ranked[2][1],
            "all_confidences":      dict(ranked),
        }
