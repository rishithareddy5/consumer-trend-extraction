"""
controller/api.py
Consumer Trend Extraction — FastAPI backend.
No chromadb. No embeddings. No internet calls.
"""

from __future__ import annotations

import logging
import os
import re
from contextlib import asynccontextmanager
from typing import List

import torch
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from peft import PeftModel
from pydantic import BaseModel, Field
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

BASE_MODEL_PATH = os.getenv("CTE_BASE_MODEL", "/opt/ai-platform/models/gemma-2-2b-it")
ADAPTER_PATH = os.getenv("CTE_ADAPTER_PATH", "/home/aiuser9/cte/adapter")
MAX_NEW_TOKENS = int(os.getenv("CTE_MAX_NEW_TOKENS", "64"))

TREND_LABELS: List[str] = [
    "rising_spicy_flavor_preference",
    "youth_driven_consumption",
    "fusion_flavor_adoption",
    "western_snack_influence",
    "health_conscious_snacking",
    "premium_packaging_demand",
    "regional_flavor_revival",
    "convenience_format_preference",
    "festive_gifting_trend",
    "online_impulse_buying",
    "sugar_free_demand",
    "protein_snack_trend",
    "small_pack_affordability_preference",
    "plant_based_adoption",
    "tangy_sour_flavor_rise",
]

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s :: %(message)s")
log = logging.getLogger("cte.api")


class TrendModel:
    def __init__(self, base_path: str, adapter_path: str):
        log.info("Loading tokenizer from %s", base_path)
        self.tokenizer = AutoTokenizer.from_pretrained(base_path)

        log.info("Loading base model in 4-bit")
        bnb = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16,
            bnb_4bit_use_double_quant=True,
        )
        base = AutoModelForCausalLM.from_pretrained(
            base_path,
            quantization_config=bnb,
            device_map="auto",
            torch_dtype=torch.bfloat16,
        )

        log.info("Attaching LoRA adapter from %s", adapter_path)
        self.model = PeftModel.from_pretrained(base, adapter_path)
        self.model.eval()
        log.info("Model ready.")

    def _build_prompt(self, feedback: str) -> str:
        user = (
            "Classify the following retailer feedback into one of these "
            f"consumer trend labels:\n{', '.join(TREND_LABELS)}\n\n"
            f"Retailer feedback: {feedback}\n\n"
            "Return ONLY the single best trend label."
        )
        return self.tokenizer.apply_chat_template(
            [{"role": "user", "content": user}],
            tokenize=False,
            add_generation_prompt=True,
        )

    @torch.inference_mode()
    def predict(self, feedback: str) -> dict:
        prompt = self._build_prompt(feedback)
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)

        gen = self.model.generate(
            **inputs,
            max_new_tokens=MAX_NEW_TOKENS,
            do_sample=False,
            return_dict_in_generate=True,
            output_scores=True,
            pad_token_id=self.tokenizer.eos_token_id,
        )

        gen_ids = gen.sequences[0][inputs["input_ids"].shape[1]:]
        decoded = self.tokenizer.decode(gen_ids, skip_special_tokens=True).strip()
        decoded_norm = re.sub(r"\s+", "_", decoded.lower())
        log.info("Greedy decode: %r", decoded)

        if gen.scores:
            probs = torch.softmax(gen.scores[0][0].float(), dim=-1)
            scored = []
            for lab in TREND_LABELS:
                ids = self.tokenizer(lab, add_special_tokens=False).input_ids
                p = float(probs[ids[0]].item()) if ids else 0.0
                scored.append((lab, p))
            total = sum(p for _, p in scored)
            if total > 0:
                scored = [(l, p / total) for l, p in scored]
        else:
            scored = [(l, 1.0 if l in decoded_norm else 0.0) for l in TREND_LABELS]

        scored.sort(key=lambda x: x[1], reverse=True)

        for i, (lab, _) in enumerate(scored):
            if lab in decoded_norm and i != 0:
                scored.insert(0, scored.pop(i))
                break

        top = scored[:3]
        while len(top) < 3:
            top.append((TREND_LABELS[len(top)], 0.0))

        return {
            "primary_trend": top[0][0],
            "primary_confidence": round(top[0][1], 4),
            "secondary_trend": top[1][0],
            "secondary_confidence": round(top[1][1], 4),
            "tertiary_trend": top[2][0],
            "tertiary_confidence": round(top[2][1], 4),
            "raw_generation": decoded,
        }


trend_model: TrendModel | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global trend_model
    trend_model = TrendModel(BASE_MODEL_PATH, ADAPTER_PATH)
    yield
    trend_model = None


app = FastAPI(
    title="Consumer Trend Extraction API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class PredictRequest(BaseModel):
    retailer_feedback: str = Field(..., min_length=3, max_length=2000)


class PredictResponse(BaseModel):
    primary_trend: str
    primary_confidence: float
    secondary_trend: str
    secondary_confidence: float
    tertiary_trend: str
    tertiary_confidence: float
    raw_generation: str | None = None


@app.get("/health")
def health():
    return {
        "status": "ok" if trend_model is not None else "loading",
        "labels": len(TREND_LABELS),
    }


@app.get("/labels")
def labels():
    return {"labels": TREND_LABELS}


@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    if trend_model is None:
        raise HTTPException(status_code=503, detail="Model is still loading.")
    try:
        return trend_model.predict(req.retailer_feedback)
    except Exception as e:
        log.exception("predict failed")
        raise HTTPException(status_code=500, detail=str(e)) from e
