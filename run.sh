#!/bin/bash
# ============================================================
# Consumer Trend Extraction System — Single Run Script
# Run this after cloning from GitHub on the GPU server
# Usage: bash run.sh
# ============================================================

set -e  # stop on any error

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

echo ""
echo "========================================================"
echo "  Consumer Trend Extraction System"
echo "  Powered by Gemma 2B + QLoRA + RAG"
echo "========================================================"
echo ""

# ── Step 1: Install dependencies ─────────────────────────────────────────────
echo "[1/6] Installing dependencies..."
pip install -r requirements.txt -q
echo "      Done."

# ── Step 2: Convert dataset to JSONL ─────────────────────────────────────────
echo "[2/6] Converting dataset to JSONL..."
python model/preprocess.py
echo "      Done."

# ── Step 3: Fine-tune Gemma 2B ───────────────────────────────────────────────
echo "[3/6] Fine-tuning Gemma 2B with QLoRA (this takes 30-60 mins)..."
python model/train.py
echo "      Done. Adapter saved to adapter/"

# ── Step 4: Build ChromaDB index ─────────────────────────────────────────────
echo "[4/6] Building ChromaDB vector index with BGE-small..."
python embeddings/embed.py
echo "      Done. Vectorstore saved to vectorstore/"

# ── Step 5: Start FastAPI ─────────────────────────────────────────────────────
echo "[5/6] Starting FastAPI on port 8000..."
uvicorn controller.api:app --host 0.0.0.0 --port 8000 &
API_PID=$!
echo "      FastAPI running (PID: $API_PID)"
sleep 5

# ── Step 6: Start Streamlit UI ────────────────────────────────────────────────
echo "[6/6] Starting Streamlit UI on port 8501..."
streamlit run view/ui.py --server.port 8501 --server.address 0.0.0.0 &
UI_PID=$!
echo "      Streamlit running (PID: $UI_PID)"

echo ""
echo "========================================================"
echo "  System is running!"
echo "  UI:     http://$(hostname -I | awk '{print $1}'):8501"
echo "  API:    http://$(hostname -I | awk '{print $1}'):8000"
echo "  MLflow: run 'mlflow ui --port 5000' in a new terminal"
echo "========================================================"
echo ""
echo "Press Ctrl+C to stop all services."

# Keep running
wait $API_PID $UI_PID
