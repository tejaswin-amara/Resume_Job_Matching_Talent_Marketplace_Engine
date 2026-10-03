"""ParallelPrimitives: Blelloch work-efficient parallel prefix-scan and tree reduction.

Implements the classic Blelloch parallel scan (Work T_1 = O(N), Span T_infinity = O(log N))
and tree-based parallel reduction with exact work-span accounting.
Zero-library constraint: built strictly on primitive arrays and bitwise indexing.
"""

from collections.abc import Callable, Sequence
from typing import NamedTuple


class ParallelMetrics(NamedTuple):
    """Execution metrics for parallel algorithmic analysis."""

    work: int  # T_1: Total operations
    span: int  # T_infinity: Critical path length (depth)
    parallelism: float  # T_1 / T_infinity


class ScanResult(NamedTuple):
    """Result of Blelloch parallel scan."""

    exclusive_scan: list[float | int]
    inclusive_scan: list[float | int]
    metrics: ParallelMetrics


class ReductionResult(NamedTuple):
    """Result of tree-based parallel reduction."""

    value: float | int
    metrics: ParallelMetrics


class ParallelPrimitives:
    """Work-efficient parallel algorithmic primitives with formal work-span tracking."""

    @staticmethod
    def _next_power_of_two(n: int) -> int:
        """Return smallest power of two >= n."""
        if n <= 1:
            return 1
        p = 1
        while p < n:
            p <<= 1
        return p

    @classmethod
    def blelloch_scan(cls, data: Sequence[float | int]) -> ScanResult:
        """Execute Blelloch work-efficient parallel prefix scan.

        Work: O(N), Span: O(log N).
        """
        n = len(data)
        if n == 0:
            return ScanResult(
                exclusive_scan=[],
                inclusive_scan=[],
                metrics=ParallelMetrics(work=0, span=0, parallelism=1.0),
            )

        m = cls._next_power_of_two(n)
        a: list[float | int] = [0] * m
        for i in range(n):
            a[i] = data[i]

        work_count = 0
        span_depth = 0

        # Phase 1: Up-sweep (reduce tree)
        step = 1
        while step < m:
            stride = step * 2
            ops_in_step = m // stride
            work_count += ops_in_step
            span_depth += 1

            for k in range(0, m, stride):
                a[k + stride - 1] += a[k + step - 1]

            step *= 2

        # Save total reduction sum
        total_sum = a[m - 1]

        # Phase 2: Down-sweep
        a[m - 1] = 0  # Set root of exclusive scan to 0
        step = m // 2
        while step > 0:
            stride = step * 2
            ops_in_step = m // stride
            work_count += 2 * ops_in_step  # 1 copy, 1 add
            span_depth += 1

            for k in range(0, m, stride):
                t = a[k + step - 1]
                a[k + step - 1] = a[k + stride - 1]
                a[k + stride - 1] += t

            step //= 2

        exclusive = a[:n]
        inclusive = [exclusive[i] + data[i] for i in range(n)]

        parallelism = float(work_count) / float(span_depth) if span_depth > 0 else 1.0
        metrics = ParallelMetrics(
            work=work_count,
            span=span_depth,
            parallelism=parallelism,
        )

        return ScanResult(
            exclusive_scan=exclusive,
            inclusive_scan=inclusive,
            metrics=metrics,
        )

    @classmethod
    def tree_reduce(
        cls,
        data: Sequence[float | int],
        op: Callable[[float | int, float | int], float | int] = lambda x, y: x + y,
    ) -> ReductionResult:
        """Tree-based parallel reduction with O(N) work and O(log N) span."""
        n = len(data)
        if n == 0:
            return ReductionResult(
                value=0,
                metrics=ParallelMetrics(work=0, span=0, parallelism=1.0),
            )
        if n == 1:
            return ReductionResult(
                value=data[0],
                metrics=ParallelMetrics(work=0, span=0, parallelism=1.0),
            )

        current = list(data)
        work_count = 0
        span_depth = 0

        while len(current) > 1:
            next_level = []
            span_depth += 1
            for i in range(0, len(current), 2):
                if i + 1 < len(current):
                    next_level.append(op(current[i], current[i + 1]))
                    work_count += 1
                else:
                    next_level.append(current[i])
            current = next_level

        parallelism = float(work_count) / float(span_depth) if span_depth > 0 else 1.0
        metrics = ParallelMetrics(
            work=work_count,
            span=span_depth,
            parallelism=parallelism,
        )

        return ReductionResult(
            value=current[0],
            metrics=metrics,
        )
