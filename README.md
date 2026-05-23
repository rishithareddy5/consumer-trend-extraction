# Consumer Trend Extraction System

> **Problem Statement:** Changing consumer preferences are often identified too late, causing OEMs to lose market momentum and miss emerging consumption trends.

**Solution:** Real-time consumer trend detection from FMCG retailer field feedback using Gemma 2B fine-tuned with QLoRA and retrieval-augmented generation (RAG).

---

## Tech Stack

| Layer | Technology |
|---|---|
| Base Model | Google Gemma 2B |
| Fine-Tuning | PEFT + LoRA |
| Quantization | 4-bit QLoRA |
| Backend | Python + FastAPI |
| UI | Streamlit |
| Data Storage | Excel / JSONL |
| Embeddings | BGE-small |
| Vector DB | ChromaDB |
| Experiment Tracking | MLflow Lite |
| GPU Runtime | CUDA + Transformers |

---

## Architecture (MVC)

```
consumer_trend_extraction/
├── data/                        ← Dataset (Excel + JSONL)
├── model/                       ← M: Gemma 2B + QLoRA
│   ├── preprocess.py            ← Excel → JSONL
│   ├── train.py                 ← Fine-tuning + MLflow
│   └── inference.py             ← Top-3 trends + confidence
├── controller/                  ← C: FastAPI
│   └── api.py                   ← Routes + RAG orchestration
├── view/                        ← V: Streamlit UI
│   └── ui.py                    ← Trend display + confidence bars
├── embeddings/                  ← BGE-small + ChromaDB
│   ├── embed.py                 ← Index 500 feedbacks
│   └── search.py                ← Similarity search (RAG)
├── adapter/                     ← LoRA weights (after training)
├── requirements.txt
├── run.sh                       ← Single script to run everything
└── README.md
```

---

## Setup & Run

### Clone on GPU server
```bash
git clone https://github.com/rishithareddy5/consumer-trend-extraction.git
cd consumer-trend-extraction
```

### Upload dataset
```bash
# Copy Excel file to data/ folder
scp -P 2222 Consumer_Trend_Extraction_Dataset.xlsx aiuser9@192.168.1.168:~/consumer-trend-extraction/data/
```

### Run everything with one command
```bash
bash run.sh
```

That's it. The script installs dependencies, trains the model, builds the index, and starts the API + UI automatically.

---

## Output Format

```json
{
  "retailer_feedback": "Kids asking for cheesy dip flavors",
  "primary_trend": "western_snack_influence",
  "primary_confidence": 0.91,
  "secondary_trend": "youth_driven_consumption",
  "secondary_confidence": 0.63,
  "tertiary_trend": "fusion_flavor_adoption",
  "tertiary_confidence": 0.34
}
```

---

## 15 Trend Labels

| # | Trend Label |
|---|---|
| 1 | rising_spicy_flavor_preference |
| 2 | youth_driven_consumption |
| 3 | fusion_flavor_adoption |
| 4 | western_snack_influence |
| 5 | health_conscious_snacking |
| 6 | premium_packaging_demand |
| 7 | regional_flavor_revival |
| 8 | convenience_format_preference |
| 9 | festive_gifting_trend |
| 10 | online_impulse_buying |
| 11 | sugar_free_demand |
| 12 | protein_snack_trend |
| 13 | small_pack_affordability_preference |
| 14 | plant_based_adoption |
| 15 | tangy_sour_flavor_rise |
