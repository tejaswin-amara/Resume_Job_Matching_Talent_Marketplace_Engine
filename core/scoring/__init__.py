from .matcher import HybridMatcher
from .skill_extractor import SkillExtractor

__all__ = ["HybridMatcher", "SkillExtractor"]


def __getattr__(name: str):
    if name == "EmbeddingService":
        from .embeddings import EmbeddingService

        return EmbeddingService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
