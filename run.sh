#!/bin/bash
# ============================================================
# Consumer Trend Extraction System — Full Run Script
# Usage: bash run.sh
# ============================================================

set -e
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

echo ""
echo "========================================================"
echo "  Consumer Trend Extraction System"
echo "  Gemma 2B + QLoRA + RAG + MVC"
echo "========================================================"
echo ""

# Step 1: Install dependencies
echo "[1/8] Installing dependencies..."
pip install -r requirements.txt -q
echo "      Done."

# Step 2: Validate dataset
echo "[2/8] Validating dataset..."
python model/validate.py
echo "      Done."

# Step 3: Train-test split + convert to JSONL
echo "[3/8] Converting dataset to JSONL (80/20 split)..."
python model/preprocess.py
echo "      Done."

# Step 4: Fine-tune Gemma 2B
echo "[4/8] Fine-tuning Gemma 2B with QLoRA (30-60 mins)..."
python model/train.py
echo "      Done. Adapter saved to adapter/"

# Step 5: Evaluate on test split
echo "[5/8] Evaluating on test split..."
python model/evaluate.py
echo "      Done. Results in data/evaluation_log.json"

# Step 6: Build ChromaDB index
echo "[6/8] Building ChromaDB vector index..."
python embeddings/embed.py
echo "      Done. Vectorstore saved."

# Step 7: Start FastAPI
echo "[7/8] Starting FastAPI on port 8000..."
uvicorn controller.api:app --host 0.0.0.0 --port 8000 &
API_PID=$!
echo "      FastAPI running (PID: $API_PID)"
sleep 5

# Step 8: Start Streamlit
echo "[8/8] Starting Streamlit UI on port 8501..."
streamlit run view/ui.py --server.port 8501 --server.address 0.0.0.0 &
UI_PID=$!
echo "      Streamlit running (PID: $UI_PID)"

echo ""
echo "========================================================"
echo "  System is running!"
echo "  UI:     http://$(hostname -I | awk '{print $1}'):8501"
echo "  API:    http://$(hostname -I | awk '{print $1}'):8000"
echo "  MLflow: mlflow ui --port 5000"
echo "========================================================"
echo ""
echo "Press Ctrl+C to stop."
wait $API_PID $UI_PID
