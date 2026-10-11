import hashlib
import math

try:
    import torch
    from sentence_transformers import SentenceTransformer

    _TORCH_AVAILABLE = True
except Exception:
    _TORCH_AVAILABLE = False


class EmbeddingService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_model()
        return cls._instance

    def _init_model(self):
        if _TORCH_AVAILABLE:
            try:
                device = "cuda" if torch.cuda.is_available() else "cpu"
                self.model = SentenceTransformer("all-MiniLM-L6-v2", device=device)
            except Exception:
                self.model = None
        else:
            self.model = None

    def _l2_normalize(self, vec: list[float]) -> list[float]:
        norm = math.sqrt(sum(x * x for x in vec))
        if norm == 0:
            if vec:
                vec[0] = 1.0
            return vec
        return [x / norm for x in vec]

    def _fallback_pseudo_embedding(self, text: str, dim: int = 384) -> list[float]:
        """Deterministic pseudo-embedding when torch is unavailable."""
        tokens = text.lower().split()
        vec = [0.0] * dim
        for tok in tokens:
            idx = int(hashlib.md5(tok.encode(), usedforsecurity=False).hexdigest(), 16) % dim
            vec[idx] += 1.0
        return self._l2_normalize(vec)

    def encode(self, text: str) -> list[float]:
        import os

        if self.model is not None:
            embedding = self.model.encode(text, convert_to_tensor=False).tolist()
            return self._l2_normalize(embedding)
        if os.environ.get("ENVIRONMENT") == "test":
            return self._fallback_pseudo_embedding(text)
        raise RuntimeError("Embedding model is unavailable. Semantic scoring cannot proceed.")

    def encode_batch(self, texts: list[str]) -> list[list[float]]:
        import os

        if self.model is not None:
            embeddings = self.model.encode(texts, convert_to_tensor=False).tolist()
            return [self._l2_normalize(emb) for emb in embeddings]
        if os.environ.get("ENVIRONMENT") == "test":
            return [self._fallback_pseudo_embedding(t) for t in texts]
        raise RuntimeError("Embedding model is unavailable. Semantic scoring cannot proceed.")
