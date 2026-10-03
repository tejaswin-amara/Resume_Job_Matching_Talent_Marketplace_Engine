"""SequenceAlignment: Needleman-Wunsch (global) and Smith-Waterman (local) alignment.

Used for career trajectory progression and experience sequence alignment.
Zero-library constraint: built with 2D DP matrices and backtrack pointers.
"""

from typing import Sequence
from typing import Any, NamedTuple, TypeVar

T = TypeVar("T")


class AlignmentResult(NamedTuple):
    """Result of sequence alignment."""

    score: float
    aligned_seq1: list[Any]
    aligned_seq2: list[Any]
    identity_rate: float


class SequenceAlignment:
    """Needleman-Wunsch (global) and Smith-Waterman (local) alignment engine."""

    GAP_SYMBOL: str = "-"

    def __init__(
        self,
        match_score: float = 2.0,
        mismatch_penalty: float = -1.0,
        gap_penalty: float = -1.0,
    ) -> None:
        self.match_score: float = match_score
        self.mismatch_penalty: float = mismatch_penalty
        self.gap_penalty: float = gap_penalty

    def _similarity(self, a: Any, b: Any) -> float:
        """Compute match/mismatch score between two elements."""
        if a == b:
            return self.match_score
        return self.mismatch_penalty

    def needleman_wunsch(self, seq1: Sequence[Any], seq2: Sequence[Any]) -> AlignmentResult:
        """Global sequence alignment using Needleman-Wunsch algorithm."""
        n = len(seq1)
        m = len(seq2)

        # dp[i][j] holds optimal global score
        dp: list[list[float]] = [[0.0] * (m + 1) for _ in range(n + 1)]

        for i in range(n + 1):
            dp[i][0] = i * self.gap_penalty
        for j in range(m + 1):
            dp[0][j] = j * self.gap_penalty

        for i in range(1, n + 1):
            for j in range(1, m + 1):
                match = dp[i - 1][j - 1] + self._similarity(seq1[i - 1], seq2[j - 1])
                delete = dp[i - 1][j] + self.gap_penalty
                insert = dp[i][j - 1] + self.gap_penalty
                dp[i][j] = max(match, delete, insert)

        # Backtrack to reconstruct alignment
        aligned1: list[Any] = []
        aligned2: list[Any] = []

        i = n
        j = m
        identical = 0
        total_cols = 0

        while i > 0 or j > 0:
            total_cols += 1
            if (
                i > 0
                and j > 0
                and dp[i][j] == dp[i - 1][j - 1] + self._similarity(seq1[i - 1], seq2[j - 1])
            ):
                aligned1.append(seq1[i - 1])
                aligned2.append(seq2[j - 1])
                if seq1[i - 1] == seq2[j - 1]:
                    identical += 1
                i -= 1
                j -= 1
            elif i > 0 and dp[i][j] == dp[i - 1][j] + self.gap_penalty:
                aligned1.append(seq1[i - 1])
                aligned2.append(self.GAP_SYMBOL)
                i -= 1
            else:
                aligned1.append(self.GAP_SYMBOL)
                aligned2.append(seq2[j - 1])
                j -= 1

        aligned1.reverse()
        aligned2.reverse()

        identity_rate = (identical / total_cols) if total_cols > 0 else 1.0
        return AlignmentResult(
            score=dp[n][m],
            aligned_seq1=aligned1,
            aligned_seq2=aligned2,
            identity_rate=identity_rate,
        )

    def smith_waterman(self, seq1: Sequence[Any], seq2: Sequence[Any]) -> AlignmentResult:
        """Local sequence alignment using Smith-Waterman algorithm."""
        n = len(seq1)
        m = len(seq2)

        dp: list[list[float]] = [[0.0] * (m + 1) for _ in range(n + 1)]

        max_score = 0.0
        max_i = 0
        max_j = 0

        for i in range(1, n + 1):
            for j in range(1, m + 1):
                match = dp[i - 1][j - 1] + self._similarity(seq1[i - 1], seq2[j - 1])
                delete = dp[i - 1][j] + self.gap_penalty
                insert = dp[i][j - 1] + self.gap_penalty
                score = max(0.0, match, delete, insert)
                dp[i][j] = score

                if score > max_score:
                    max_score = score
                    max_i = i
                    max_j = j

        # Backtrack from (max_i, max_j) until cell reaches 0.0
        aligned1: list[Any] = []
        aligned2: list[Any] = []

        curr_i = max_i
        curr_j = max_j
        identical = 0
        total_cols = 0

        while curr_i > 0 and curr_j > 0 and dp[curr_i][curr_j] > 0.0:
            total_cols += 1
            sim = self._similarity(seq1[curr_i - 1], seq2[curr_j - 1])
            if dp[curr_i][curr_j] == dp[curr_i - 1][curr_j - 1] + sim:
                aligned1.append(seq1[curr_i - 1])
                aligned2.append(seq2[curr_j - 1])
                if seq1[curr_i - 1] == seq2[curr_j - 1]:
                    identical += 1
                curr_i -= 1
                curr_j -= 1
            elif dp[curr_i][curr_j] == dp[curr_i - 1][curr_j] + self.gap_penalty:
                aligned1.append(seq1[curr_i - 1])
                aligned2.append(self.GAP_SYMBOL)
                curr_i -= 1
            else:
                aligned1.append(self.GAP_SYMBOL)
                aligned2.append(seq2[curr_j - 1])
                curr_j -= 1

        aligned1.reverse()
        aligned2.reverse()

        identity_rate = (identical / total_cols) if total_cols > 0 else 0.0
        return AlignmentResult(
            score=max_score,
            aligned_seq1=aligned1,
            aligned_seq2=aligned2,
            identity_rate=identity_rate,
        )
