try:
    import faiss
except Exception:  # pragma: no cover - optional dependency
    faiss = None
import numpy as np


class VectorDB:
    """Simple FAISS-based vector storage for embeddings."""

    def __init__(self, dim: int):
        if faiss is None:
            raise ImportError("faiss is required for VectorDB")
        self.index = faiss.IndexFlatL2(dim)
        self.meta = []

    def add(self, embedding, info):
        vec = np.asarray([embedding], dtype='float32')
        self.index.add(vec)
        self.meta.append(info)

    def search(self, embedding, k: int = 5):
        vec = np.asarray([embedding], dtype='float32')
        distances, ids = self.index.search(vec, k)
        results = []
        for i in ids[0]:
            if i < len(self.meta):
                results.append(self.meta[i])
        return results
