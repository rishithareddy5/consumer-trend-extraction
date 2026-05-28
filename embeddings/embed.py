"""
embeddings/embed.py
Indexes all 500 retailer feedbacks into ChromaDB using BGE-small.
Run once after dataset is ready.
Run: python embeddings/embed.py
"""
import pandas as pd
import chromadb
from pathlib import Path
from sentence_transformers import SentenceTransformer

ROOT       = Path(__file__).resolve().parent.parent
EXCEL_PATH = ROOT / "data" / "Consumer_Trend_Extraction_Dataset.xlsx"
VECTOR_DIR = ROOT / "vectorstore"
EMBED_MODEL = "BAAI/bge-small-en-v1.5"


def build_index():
    print("[embed] Loading dataset...")
    df = pd.read_excel(EXCEL_PATH, sheet_name="Training_Dataset")

    print("[embed] Loading BGE-small embedder...")
    embedder = SentenceTransformer(EMBED_MODEL)

    print(f"[embed] Generating embeddings for {len(df)} feedbacks...")
    embeddings = embedder.encode(
        df["retailer_feedback"].tolist(),
        show_progress_bar=True
    ).tolist()

    VECTOR_DIR.mkdir(parents=True, exist_ok=True)
    client     = chromadb.PersistentClient(path=str(VECTOR_DIR))
    collection = client.get_or_create_collection(
        name="retailer_feedbacks",
        metadata={"hnsw:space": "cosine"}
    )

    # Clear existing if re-indexing
    if collection.count() > 0:
        collection.delete(ids=collection.get()["ids"])
        print("[embed] Cleared existing index.")

    collection.add(
        embeddings=embeddings,
        documents=df["retailer_feedback"].tolist(),
        metadatas=[{
            "trend":       row["trend_label"],
            "city":        str(row["city"]),
            "season":      str(row["season"]),
            "store_type":  str(row["store_type"]),
            "demographic": str(row["consumer_demographic"]),
            "record_id":   str(row["record_id"]),
        } for _, row in df.iterrows()],
        ids=[str(row["record_id"]) for _, row in df.iterrows()],
    )

    print(f"[embed] Index built — {collection.count()} records in ChromaDB.")
    print(f"[embed] Vectorstore saved → {VECTOR_DIR}")


if __name__ == "__main__":
    build_index()
