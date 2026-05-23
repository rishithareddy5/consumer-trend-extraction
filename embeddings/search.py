"""
embeddings/search.py
Searches ChromaDB for similar retailer feedbacks.
Used by controller to provide RAG context to Gemma.
"""
import chromadb
from pathlib import Path
from sentence_transformers import SentenceTransformer

ROOT        = Path(__file__).resolve().parent.parent
VECTOR_DIR  = ROOT / "vectorstore"
EMBED_MODEL = "BAAI/bge-small-en-v1.5"


class SimilaritySearcher:
    def __init__(self):
        print("[search] Loading BGE-small + ChromaDB...")
        self.embedder   = SentenceTransformer(EMBED_MODEL)
        self.client     = chromadb.PersistentClient(path=str(VECTOR_DIR))
        self.collection = self.client.get_collection("retailer_feedbacks")
        print(f"[search] Ready — {self.collection.count()} records indexed.")

    def search(self, query: str, n: int = 3) -> list:
        """Find n most similar feedbacks. Returns list of dicts."""
        embedding = self.embedder.encode([query]).tolist()
        results   = self.collection.query(
            query_embeddings=embedding,
            n_results=n,
            include=["documents", "metadatas", "distances"],
        )
        output = []
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            output.append({
                "feedback":   doc,
                "trend":      meta["trend"],
                "city":       meta.get("city", ""),
                "season":     meta.get("season", ""),
                "similarity": round(1 - dist, 4),
            })
        return output
