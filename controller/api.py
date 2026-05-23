"""
controller/api.py
FastAPI controller — MVC Controller layer.
Receives feedback → searches ChromaDB → calls Gemma → returns top-3 trends.
Run: uvicorn controller.api:app --host 0.0.0.0 --port 8000 --reload
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
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

# Load once at startup
print("[api] Initializing...")
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
    primary_trend:        str
    primary_confidence:   float
    secondary_trend:      str
    secondary_confidence: float
    tertiary_trend:       str
    tertiary_confidence:  float
    similar_examples:     list
    all_confidences:      dict


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
    Main endpoint:
    1. ChromaDB finds 3 similar feedbacks (RAG context)
    2. Gemma classifies with context
    3. Returns top-3 trends with confidence scores
    """
    if not req.retailer_feedback.strip():
        raise HTTPException(status_code=400, detail="retailer_feedback cannot be empty")

    # RAG — get similar examples
    try:
        similar = searcher.search(req.retailer_feedback, n=3)
    except Exception as e:
        similar = []
        print(f"[api] ChromaDB search error: {e}")

    # Gemma inference
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

    return TrendResponse(
        retailer_feedback=req.retailer_feedback,
        primary_trend=result["primary_trend"],
        primary_confidence=result["primary_confidence"],
        secondary_trend=result["secondary_trend"],
        secondary_confidence=result["secondary_confidence"],
        tertiary_trend=result["tertiary_trend"],
        tertiary_confidence=result["tertiary_confidence"],
        similar_examples=similar,
        all_confidences=result["all_confidences"],
    )
