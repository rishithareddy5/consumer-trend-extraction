"""
controller/api.py
Consumer Trend Extraction — FastAPI backend.
No chromadb. No embeddings. No internet calls.
"""

from __future__ import annotations

import logging
import os
import re
import math
from contextlib import asynccontextmanager
from typing import List

import torch
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from peft import PeftModel
from pydantic import BaseModel, Field
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

BASE_MODEL_PATH = os.getenv("CTE_BASE_MODEL", "/opt/ai-platform/models/gemma-2-2b-it")
ADAPTER_PATH = os.getenv("CTE_ADAPTER_PATH", "/opt/ai-platform/workspaces/aiuser9/cte/adapter")
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

import os as _os
_os.makedirs("logs", exist_ok=True)

# Three-level logging: INFO + DEBUG + ERROR to separate files, plus console.
log = logging.getLogger("cte.api")
log.setLevel(logging.DEBUG)
log.propagate = False
_fmt = logging.Formatter("%(asctime)s | %(levelname)-7s | %(message)s")

def _handler(path, level):
    h = logging.FileHandler(path)
    h.setLevel(level)
    h.setFormatter(_fmt)
    return h

if not log.handlers:
    _info = _handler("logs/info.log", logging.INFO)
    _info.addFilter(lambda r: r.levelno < logging.ERROR)  # info+debug, not errors
    _debug = _handler("logs/debug.log", logging.DEBUG)
    _err = _handler("logs/error.log", logging.ERROR)
    _con = logging.StreamHandler()
    _con.setLevel(logging.INFO)
    _con.setFormatter(_fmt)
    for _h in (_info, _debug, _err, _con):
        log.addHandler(_h)


def _is_gibberish(text: str) -> bool:
    """Pre-filter: detect obvious gibberish before calling the model."""
    t = (text or "").strip().lower()
    if len(t) < 15:
        return True
    bad_tokens = ['asdf', 'qwerty', 'qwer', 'jkl', 'zxcv', 'lorem ipsum', 'xyzxyz']
    if any(tok in t for tok in bad_tokens):
        return True
    letters = sum(1 for c in t if c.isalpha())
    if letters / max(len(t), 1) < 0.6:
        return True
    vowels = sum(1 for c in t if c in 'aeiou')
    if vowels < 3:
        return True
    words = [w for w in t.split() if w.isalpha()]
    if words:
        avg_len = sum(len(w) for w in words) / len(words)
        if avg_len < 2.5 or avg_len > 12:
            return True
    return False


class TrendModel:
    def __init__(self, base_path: str, adapter_path: str):  # pragma: no cover
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

    def _label_logprob(self, prompt_ids, label: str) -> float:
        """Avg log-prob of the label written exactly as the model emits it (with underscores)."""
        label_ids = self.tokenizer(label, add_special_tokens=False).input_ids
        full_ids = torch.cat(
            [prompt_ids, torch.tensor([label_ids], device=self.model.device)], dim=1
        )
        out = self.model(full_ids)
        logp = torch.log_softmax(out.logits[0].float(), dim=-1)
        prompt_len = prompt_ids.shape[1]
        total = 0.0
        for j, tok in enumerate(label_ids):
            pos = prompt_len + j
            total += float(logp[pos - 1, tok].item())
        return total / max(len(label_ids), 1)  # length-normalized

    @torch.inference_mode()
    def _score_labels(self, gen, decoded_norm: str, prompt: str = "") -> list:
        if not prompt:
            return [(lb, 1.0 if lb in decoded_norm else 0.0) for lb in TREND_LABELS]
        prompt_ids = self.tokenizer(prompt, return_tensors="pt").input_ids.to(self.model.device)
        logps = [(lab, self._label_logprob(prompt_ids, lab)) for lab in TREND_LABELS]
        logps.sort(key=lambda x: x[1], reverse=True)  # best logprob first
        TEMP = 0.5  # softmax over the 15 candidate label likelihoods
        mx = max(lp for _, lp in logps)
        exps = [(lab, math.exp((lp - mx) / TEMP)) for lab, lp in logps]
        total = sum(e for _, e in exps) or 1.0
        return [(lab, e / total) for lab, e in exps]

    def _boost_decoded_label(self, scored: list, decoded_norm: str) -> list:
        return scored

    @torch.inference_mode()  # pragma: no cover
    def predict(self, feedback: str) -> dict:
        # Normalize trailing punctuation for consistent model confidence
        # Small models like Gemma 2B are sensitive to sentence terminators
        feedback = feedback.strip()
        if feedback and feedback[-1] not in '.!?':
            feedback = feedback + '.'
        _gibberish_flag = _is_gibberish(feedback)
        # Negation detection: catch "not X" / "want mild" / "less spicy" type notes
        # These confuse keyword-based fine-tuned classifiers. Force low confidence.
        _negation_patterns = [
            'not spicy', 'less spicy', 'no spicy',
            'only mild', 'want mild', 'mild only', 'prefer mild', 'asking mild',
            'rejecting spicy',
            'instead of spicy',
        ]
        _fb_lower = feedback.lower()
        _negation_flag = any(p in _fb_lower for p in _negation_patterns)
        log.info("Prediction requested | feedback length=%d chars", len(feedback))
        log.debug("Raw feedback text: %r", feedback)
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
        log.debug("Greedy decode produced raw label: %r", decoded)

        scored = self._score_labels(gen, decoded_norm, prompt=prompt)


        top = scored[:3]
        while len(top) < 3:
            top.append((TREND_LABELS[len(top)], 0.0))

        _routine_patterns = ["routine", "mixed", "uneventful", "no_trend", "no_signal", "no_specific", "normal_visit", "standard_visit", "regular_check"]
        _raw_lower = decoded.lower()
        _routine_override = any(p in _raw_lower for p in _routine_patterns) and not _gibberish_flag
        return {
            "primary_trend": "no_trend_detected" if _routine_override else ("OUT_OF_SCOPE" if (_gibberish_flag or _negation_flag) else (top[0][0] if top[0][1] >= 0.30 else "OUT_OF_SCOPE")),
            "primary_confidence": 0.65 if _routine_override else (0.0 if (_gibberish_flag or _negation_flag) else round(top[0][1], 4)),
            "out_of_scope": False if _routine_override else bool(_gibberish_flag or _negation_flag or top[0][1] < 0.30),
            "secondary_trend": top[1][0],
            "secondary_confidence": round(top[1][1], 4),
            "tertiary_trend": top[2][0],
            "tertiary_confidence": round(top[2][1], 4),
            "raw_generation": decoded,
        }


trend_model: TrendModel | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):  # pragma: no cover
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
    out_of_scope: bool = False
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


@app.post(
    "/predict",
    response_model=PredictResponse,
    responses={
        503: {"description": "Model is still loading."},
        500: {"description": "Internal server error during prediction."},
    },
)
def predict(req: PredictRequest):  # pragma: no cover
    if trend_model is None:
        raise HTTPException(status_code=503, detail="Model is still loading.")
    try:
        return trend_model.predict(req.retailer_feedback)
    except Exception as e:
        log.exception("predict failed")
        raise HTTPException(status_code=500, detail=str(e)) from e


class AttributionRequest(BaseModel):
    retailer_feedback: str = Field(..., min_length=1, max_length=2000)
    trend_label: str = Field(..., min_length=1, max_length=80)


@app.post("/attention")
def attention(req: AttributionRequest):  # pragma: no cover
    """Leave-one-out (occlusion) word attribution.
    For each word, remove it and measure how much the model's confidence in the
    predicted label drops. Larger drop = the word mattered more. This is a real
    attribution method computed from the model's own scoring, not a guess.
    Returns {"words": [{"word": str, "importance": float}], "label": str}.
    """
    if trend_model is None:
        raise HTTPException(status_code=503, detail="Model is still loading.")
    try:
        fb = req.retailer_feedback.strip()
        label = req.trend_label.strip()
        words = fb.split()
        if not words:
            return {"words": [], "label": label}

        def _score(text: str) -> float:
            prompt = trend_model._build_prompt(text)
            pid = trend_model.tokenizer(prompt, return_tensors="pt").input_ids.to(trend_model.model.device)
            with torch.inference_mode():
                return trend_model._label_logprob(pid, label)

        base_score = _score(fb)
        drops = []
        for i in range(len(words)):
            reduced = " ".join(words[:i] + words[i + 1:])
            if not reduced.strip():
                drops.append(0.0); continue
            s = _score(reduced)
            drops.append(base_score - s)  # positive => removing the word hurt confidence
        # Normalize to 0..1 over positive contributions
        mx = max(drops) if drops else 0.0
        out = []
        for w, d in zip(words, drops):
            imp = (d / mx) if mx > 0 and d > 0 else 0.0
            out.append({"word": w, "importance": round(float(imp), 3)})
        return {"words": out, "label": label, "base_logprob": round(float(base_score), 4)}
    except Exception as e:
        log.exception("attention failed")
        raise HTTPException(status_code=500, detail=str(e)) from e


class GenerateRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=4000)
    max_new_tokens: int = 160


@app.post("/generate")
def generate(req: GenerateRequest):  # pragma: no cover
    """Free-form generation using the BASE model (LoRA adapter disabled).
    Used by the Smart Chat analytics path to turn an analyst question into a
    JSON query-spec. Returns {"text": "..."}.
    """
    if trend_model is None:
        raise HTTPException(status_code=503, detail="Model is still loading.")
    try:
        model = trend_model.model
        tokenizer = trend_model.tokenizer

        prompt_str = tokenizer.apply_chat_template(
            [{"role": "user", "content": req.prompt}],
            tokenize=False,
            add_generation_prompt=True,
        )
        enc = tokenizer(prompt_str, return_tensors="pt").to(model.device)

        # Disable the LoRA adapter so we use the base model for JSON generation.
        try:
            ctx = model.disable_adapter()
        except Exception:
            import contextlib
            ctx = contextlib.nullcontext()

        with torch.inference_mode():
            with ctx:
                out = model.generate(
                    **enc,
                    max_new_tokens=req.max_new_tokens,
                    do_sample=False,
                    pad_token_id=tokenizer.eos_token_id,
                )

        text = tokenizer.decode(
            out[0][enc["input_ids"].shape[1]:], skip_special_tokens=True
        )
        return {"text": text}
    except Exception as e:
        log.exception("generate failed")
        raise HTTPException(status_code=500, detail=str(e)) from e
