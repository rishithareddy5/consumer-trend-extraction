"""
controller/api.py
FastAPI controller — MVC Controller layer.
Receives feedback → ChromaDB similarity guard → Gemma inference guard → returns result.
Run: uvicorn controller.api:app --host 0.0.0.0 --port 8000 --reload
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
from model.inference import TrendPredictor
from embeddings.search import SimilaritySearcher

app = FastAPI(
    title="Consumer Trend Extraction API",
    description="Detects emerging FMCG consumer trends from retailer feedback — Gemma 2B + QLoRA + RAG",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Thresholds ─────────────────────────────────────────────────────────────────
SIMILARITY_THRESHOLD  = 0.40   # ChromaDB: below this = not retailer feedback
CONFIDENCE_THRESHOLD  = 0.45   # Gemma: below this = too uncertain to classify

# ── Load once at startup ───────────────────────────────────────────────────────
print("[api] Initializing model and vectorstore...")
predictor = TrendPredictor()
searcher  = SimilaritySearcher()
print("[api] Ready to serve.")


# ── Schemas ───────────────────────────────────────────────────────────────────
class FeedbackRequest(BaseModel):
    retailer_feedback:    str = Field(..., description="Raw salesperson observation")
    city:                 str = Field(default="")
    store_type:           str = Field(default="")
    consumer_demographic: str = Field(default="")
    season:               str = Field(default="")


class TrendResponse(BaseModel):
    retailer_feedback:    str
    status:               str          # "success" | "no_trend_detected" | "low_confidence"
    message:              str
    primary_trend:        Optional[str]
    primary_confidence:   Optional[float]
    secondary_trend:      Optional[str]
    secondary_confidence: Optional[float]
    tertiary_trend:       Optional[str]
    tertiary_confidence:  Optional[float]
    similar_examples:     list
    all_confidences:      Optional[dict]


# ── Endpoints ─────────────────────────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok", "model": "gemma-2b-lora", "version": "1.0.0"}


@app.get("/trends")
def list_trends():
    from model.inference import VALID_TRENDS
    return {"trends": VALID_TRENDS, "count": len(VALID_TRENDS)}


@app.post("/predict", response_model=TrendResponse)
def predict(req: FeedbackRequest):
    """
    Main prediction endpoint with two-level guard:

    Guard 1 — ChromaDB similarity check:
      If best match similarity < 0.40 → not retailer feedback → reject early

    Guard 2 — Gemma confidence check:
      If top confidence < 0.45 → too uncertain → return low_confidence status

    Only if both guards pass → return full top-3 trends with confidence scores.
    """

    # ── Basic input validation ─────────────────────────────────────────────────
    if not req.retailer_feedback.strip():
        raise HTTPException(status_code=400, detail="retailer_feedback cannot be empty")

    if len(req.retailer_feedback.strip()) < 10:
        raise HTTPException(status_code=400, detail="retailer_feedback too short to analyze")

    # ── Step 1: ChromaDB similarity search ────────────────────────────────────
    try:
        similar = searcher.search(req.retailer_feedback, n=3)
    except Exception as e:
        similar = []
        print(f"[api] ChromaDB error: {e}")

    # ── Guard 1: Similarity threshold ─────────────────────────────────────────
    top_similarity = similar[0]["similarity"] if similar else 0.0

    if top_similarity < SIMILARITY_THRESHOLD:
        return TrendResponse(
            retailer_feedback=req.retailer_feedback,
            status="no_trend_detected",
            message=(
                "This input does not appear to be retailer feedback. "
                "No recognizable consumer trend signal was found. "
                "Please enter a field observation from a salesperson "
                "(e.g. 'Retailer says customers asking for spicy variants')."
            ),
            primary_trend=None,
            primary_confidence=None,
            secondary_trend=None,
            secondary_confidence=None,
            tertiary_trend=None,
            tertiary_confidence=None,
            similar_examples=similar,
            all_confidences=None,
        )

    # ── Step 2: Gemma inference ───────────────────────────────────────────────
    try:
        result = predictor.predict(
            feedback=req.retailer_feedback,
            city=req.city,
            store_type=req.store_type,
            demographic=req.consumer_demographic,
            season=req.season,
            context_examples=similar,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference failed: {str(e)}")

    # ── Guard 2: Confidence threshold ─────────────────────────────────────────
    if result["primary_confidence"] < CONFIDENCE_THRESHOLD:
        return TrendResponse(
            retailer_feedback=req.retailer_feedback,
            status="low_confidence",
            message=(
                f"Input detected as possible retailer feedback "
                f"(similarity: {round(top_similarity*100)}%) "
                f"but model confidence is too low to classify reliably "
                f"({round(result['primary_confidence']*100)}%). "
                f"This may be outside the scope of the 15 known trend categories."
            ),
            primary_trend=result["primary_trend"],
            primary_confidence=result["primary_confidence"],
            secondary_trend=result["secondary_trend"],
            secondary_confidence=result["secondary_confidence"],
            tertiary_trend=result["tertiary_trend"],
            tertiary_confidence=result["tertiary_confidence"],
            similar_examples=similar,
            all_confidences=result["all_confidences"],
        )

    # ── Success: both guards passed ───────────────────────────────────────────
    return TrendResponse(
        retailer_feedback=req.retailer_feedback,
        status="success",
        message="Consumer trend detected successfully.",
        primary_trend=result["primary_trend"],
        primary_confidence=result["primary_confidence"],
        secondary_trend=result["secondary_trend"],
        secondary_confidence=result["secondary_confidence"],
        tertiary_trend=result["tertiary_trend"],
        tertiary_confidence=result["tertiary_confidence"],
        similar_examples=similar,
        all_confidences=result["all_confidences"],
    )