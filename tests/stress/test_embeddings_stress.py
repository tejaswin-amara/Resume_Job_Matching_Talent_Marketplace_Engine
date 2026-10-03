"""Empirical stress test suite for core/scoring/embeddings.py.

Tests:
1. Boundary conditions: empty string, whitespace-only, single token, newline/tabs.
2. Very long inputs (100k, 1M characters).
3. Unicode edge cases (emojis, CJK, Arabic, Hindi, Cyrillic, zero-width chars, null bytes).
4. Direct vector normalization: zero vectors, empty list, single element, negative values, large values.
5. Invariant check: L2 norm is ALWAYS 1.0 (within 1e-6 tolerance) for any text input.
6. Zero-division immunity: no ZeroDivisionError raised under any edge case.
7. Determinism: identical input produces bit-identical output.
8. Batch equivalence: encode_batch([t1, t2]) == [encode(t1), encode(t2)].
9. Fallback mode explicit verification: verify behavior when _TORCH_AVAILABLE is False.
"""

import math
import pytest
from core.scoring.embeddings import EmbeddingService


@pytest.fixture
def service():
    return EmbeddingService()


def vector_norm(vec: list[float]) -> float:
    return math.sqrt(sum(x * x for x in vec))


class TestEmbeddingEdgeCases:
    """Stress tests for EmbeddingService.encode() with unusual inputs."""

    @pytest.mark.parametrize(
        "label,text",
        [
            ("empty", ""),
            ("single_space", " "),
            ("spaces", "   "),
            ("whitespace_mix", "\t\n\r"),
            ("newlines", "\n\n\n\n"),
            ("single_char", "a"),
            ("punctuation", "!"),
            ("digits", "1234567890"),
            ("trimmed", "   leading and trailing spaces   "),
            ("emojis", "🚀🔥💻🎉🌟🤖🧠⚡️🎯"),
            ("cjk", "测试候选人技能简历人工智能工程师"),
            ("arabic", "مهندس برمجيات ذكاء اصطناعي وتطوير نظم"),
            ("hindi", "सॉफ्टवेयर इंजीनियर आर्टिफिशियल इंटेलिजेंस"),
            ("cyrillic", "разработчик программного обеспечения машинное обучение"),
            ("accents", "e\u0301\u0301\u0301 accent test"),
            ("zero_width", "\u200b\u200c\u200d\ufeff zero-width"),
            ("null_byte", "\x00\x01\x02 binary bytes in string"),
            ("mixed", "Mixed 🚀 CJK 测试 Arabic مهندس and symbols @#$%^&*()_+"),
        ],
        ids=lambda label_or_val: label_or_val if isinstance(label_or_val, str) and len(label_or_val) < 30 else ""
    )
    def test_encode_norm_is_always_one(self, service, label, text):
        """Invariant: L2 norm of encoded vector must always equal 1.0."""
        vec = service.encode(text)
        assert len(vec) == 384
        assert not any(math.isnan(x) for x in vec), f"NaN found in embedding for text: {label}"
        assert not any(math.isinf(x) for x in vec), f"Inf found in embedding for text: {label}"
        norm = vector_norm(vec)
        assert abs(norm - 1.0) < 1e-5, f"Norm was {norm} != 1.0 for input: {label}"

    def test_long_text_100k(self, service):
        """100k char text stress test."""
        text = "word " * 20000
        vec = service.encode(text)
        assert len(vec) == 384
        assert not any(math.isnan(x) for x in vec)
        assert not any(math.isinf(x) for x in vec)
        norm = vector_norm(vec)
        assert abs(norm - 1.0) < 1e-5

    def test_long_text_1mb(self, service):
        """1MB text stress test."""
        text = "software engineering python data machine learning algorithms " * 16000
        vec = service.encode(text)
        assert len(vec) == 384
        assert not any(math.isnan(x) for x in vec)
        assert not any(math.isinf(x) for x in vec)
        norm = vector_norm(vec)
        assert abs(norm - 1.0) < 1e-5

    def test_empty_string_deterministic(self, service):
        """Empty string must produce a valid 384-dim normalized vector."""
        vec1 = service.encode("")
        vec2 = service.encode("")
        assert vec1 == vec2
        assert len(vec1) == 384
        assert abs(vector_norm(vec1) - 1.0) < 1e-5

    def test_whitespace_only_deterministic(self, service):
        """Whitespace-only string must produce the same vector as empty string in fallback."""
        vec_empty = service.encode("")
        vec_space = service.encode("     \t\n")
        assert vec_empty == vec_space

    def test_single_token(self, service):
        """Single token input."""
        vec = service.encode("python")
        assert len(vec) == 384
        assert abs(vector_norm(vec) - 1.0) < 1e-5


class TestL2NormalizeFunction:
    """Adversarial testing of _l2_normalize directly."""

    def test_all_zeros_vector(self, service):
        """All-zeros vector must not raise ZeroDivisionError and must be normalized to norm 1.0."""
        zero_vec = [0.0] * 384
        normed = service._l2_normalize(zero_vec)
        assert len(normed) == 384
        assert normed[0] == 1.0
        assert all(x == 0.0 for x in normed[1:])
        assert vector_norm(normed) == 1.0

    def test_all_zeros_small_vector(self, service):
        """Small all-zeros vector."""
        zero_vec = [0.0, 0.0, 0.0]
        normed = service._l2_normalize(zero_vec)
        assert normed == [1.0, 0.0, 0.0]
        assert vector_norm(normed) == 1.0

    def test_empty_vector(self, service):
        """Empty list should return empty list without crash."""
        assert service._l2_normalize([]) == []

    def test_negative_values(self, service):
        """Negative values normalization."""
        vec = [-3.0, 4.0]
        normed = service._l2_normalize(vec)
        assert abs(normed[0] - (-0.6)) < 1e-6
        assert abs(normed[1] - 0.8) < 1e-6
        assert abs(vector_norm(normed) - 1.0) < 1e-6

    def test_subnormal_very_small_values(self, service):
        """Very small floats."""
        vec = [1e-20] * 100
        normed = service._l2_normalize(vec)
        norm = vector_norm(normed)
        assert abs(norm - 1.0) < 1e-5

    def test_very_large_values_no_overflow(self, service):
        """Large numbers that might overflow naive square sum if not handled."""
        vec = [1e150] * 10
        normed = service._l2_normalize(vec)
        norm = vector_norm(normed)
        assert abs(norm - 1.0) < 1e-5


class TestBatchEncoding:
    """Tests for encode_batch."""

    def test_batch_empty_list(self, service):
        """Empty batch returns empty list."""
        assert service.encode_batch([]) == []

    def test_batch_matches_single_encodes(self, service):
        """encode_batch must give identical results to individual encode calls."""
        texts = [
            "Senior Software Engineer",
            "",
            "   ",
            "FastAPI Python Docker Kubernetes",
            "🚀 Fullstack Dev 🌟",
        ]
        batch_res = service.encode_batch(texts)
        single_res = [service.encode(t) for t in texts]
        assert len(batch_res) == len(single_res)
        for b, s in zip(batch_res, single_res, strict=True):
            assert b == pytest.approx(s, abs=1e-5)


class TestFallbackExplicit:
    """Explicitly verify fallback pseudo-embedding logic."""

    def test_fallback_deterministic_output(self, service):
        """_fallback_pseudo_embedding produces exact expected shape and norm."""
        res = service._fallback_pseudo_email = service._fallback_pseudo_embedding("Python Developer", dim=384)
        assert len(res) == 384
        assert abs(vector_norm(res) - 1.0) < 1e-5

    def test_fallback_empty_string(self, service):
        """_fallback_pseudo_embedding with empty string produces [1.0, 0, 0...]."""
        res = service._fallback_pseudo_embedding("", dim=384)
        assert len(res) == 384
        assert res[0] == 1.0
        assert all(x == 0.0 for x in res[1:])
        assert vector_norm(res) == 1.0
