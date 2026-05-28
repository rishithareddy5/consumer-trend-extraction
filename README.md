# Consumer Trend Extraction System (Use Case 6)

Problem: Changing consumer preferences are often identified too late, causing OEMs to lose market momentum. This system infers emerging consumer trends from FMCG retailer field feedback collected by sales representatives.

Solution: A 15-class consumer-trend classifier built on Google Gemma 2B IT, fine-tuned with QLoRA, served via FastAPI with a Streamlit UI.

## Tech Stack
- Base Model: Google Gemma 2B IT
- Fine-Tuning: PEFT + LoRA (r=16, alpha=32)
- Quantization: 4-bit QLoRA (nf4)
- Backend: Python 3.12 + FastAPI
- UI: Streamlit
- Data Storage: CSV / JSONL
- Experiment Tracking: MLflow
- GPU Runtime: NVIDIA L40S, CUDA + Transformers

Note: embeddings/vector DB are optional and not used. This is a direct classification task, so no retrieval step is required.

## Results (measured on 105 held-out test records)
- Top-1 accuracy: 80.95% (85/105), evaluated on a test set the model never saw during training.
- Reliability: 10/10 identical output for identical input across shuffled-order and out-of-distribution probe tests (greedy decoding, fully deterministic).
- Confidence is a softmax over all 15 labels, so it is a relative ranking (about 6.7% would be random).
- Remaining errors are confusions between semantically overlapping trends (e.g. western_snack vs youth_driven), never nonsense predictions.

## Iterative Improvement
Weak classes identified via per-class evaluation (western_snack, festive_gifting) were improved by adding targeted contrast training examples and retraining, then re-evaluated on the same held-out set. This demonstrates the scalability path: adding training data improves the model without breaking it.

## Reliability Testing
The reliability test asks 10 questions in order, repeats them in shuffled order, and injects out-of-distribution probes between them. A pass requires every question to return an identical label and confidence on both passes. Current result: 10/10 identical.
Command: python tests/test_reliability.py --api http://localhost:8000

## Code Quality (SonarQube)
- Quality Gate: PASSED
- Security: A
- Reliability: A
- Maintainability: A
- Coverage: 86.4%
- Duplications: 0.0%

## Architecture (MVC)
- data/        Dataset: dataset.csv, train.jsonl, test.jsonl
- model/       train.py (QLoRA), inference.py, evaluate.py
- controller/  FastAPI: api.py (routes + prediction)
- view/        Streamlit UI: ui.py
- adapter/     Trained LoRA adapter weights
- tests/       Unit + reliability tests

## How to Run
Server: aiuser9@10.40.252.14 (NVIDIA L40S)
1. source /opt/ai-platform/venv/bin/activate
2. cd /opt/ai-platform/workspaces/aiuser9/cte
3. Terminal 1: uvicorn controller.api:app --host 0.0.0.0 --port 8000
4. Terminal 2: streamlit run view/ui.py --server.port 8519 --server.address 0.0.0.0
5. SSH tunnel: ssh -L 8519:localhost:8519 aiuser9@10.40.252.14
6. Open http://localhost:8519

## Retrain
- python model/train.py
- python model/evaluate.py
- python tests/test_reliability.py --api http://localhost:8000

## Output Format
Keys returned: primary_trend, primary_confidence, secondary_trend, secondary_confidence, tertiary_trend, tertiary_confidence. Example primary: rising_spicy_flavor_preference at 0.71 confidence.

## 15 Trend Labels
rising_spicy_flavor_preference, youth_driven_consumption, fusion_flavor_adoption, western_snack_influence, health_conscious_snacking, premium_packaging_demand, regional_flavor_revival, convenience_format_preference, festive_gifting_trend, online_impulse_buying, sugar_free_demand, protein_snack_trend, small_pack_affordability_preference, plant_based_adoption, tangy_sour_flavor_rise
