"""Latency measurement primitives for the perception -> action pipeline.

The hard requirement (DECISIONS.md / plan): end-to-end p95 < 50 ms on the real
pipeline. This module provides the percentile machinery, per-stage timing, and the
budget spec so the number is honest and reproducible from day one. The runnable
harness lives in ``benchmarks/latency.py``; the logic lives here so it is unit-tested
and coverage-counted.

No-op-backend timings only exercise glue code (sub-budget < 5 ms); the real cost
(MediaPipe inference + capture) is measured once recorded frames exist (plan Step 6a).
"""

from __future__ import annotations

import time
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field

# Ordered pipeline stages. End-to-end latency = sum of these per frame.
STAGES: tuple[str, ...] = (
    "capture",
    "inference",
    "landmark_to_gesture",
    "resolve",
    "dispatch",
    "os_call",
)

# Stages that are pure glue (no model inference, no real device I/O). Their summed
# p95 is the "glue sub-budget" measurable on the no-op backend before any modality.
GLUE_STAGES: frozenset[str] = frozenset({"landmark_to_gesture", "resolve", "dispatch"})


def percentile(values: list[float], q: float) -> float:
    """Linear-interpolation percentile (q in [0, 100]). Empty -> 0.0."""
    if not values:
        return 0.0
    if not 0.0 <= q <= 100.0:
        raise ValueError(f"percentile q must be in [0, 100], got {q}")
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    rank = (q / 100.0) * (len(ordered) - 1)
    low = int(rank)
    high = min(low + 1, len(ordered) - 1)
    frac = rank - low
    return ordered[low] + (ordered[high] - ordered[low]) * frac


@dataclass
class Recorder:
    """Collects per-frame, per-stage timings in milliseconds."""

    iterations: list[dict[str, float]] = field(default_factory=list)
    _current: dict[str, float] = field(default_factory=dict)

    @contextmanager
    def frame(self) -> Iterator[Recorder]:
        """Open a new frame; stage timings recorded inside are grouped together."""
        self._current = {}
        try:
            yield self
        finally:
            self.iterations.append(self._current)
            self._current = {}

    @contextmanager
    def stage(self, name: str) -> Iterator[None]:
        """Time a stage within the current frame."""
        if name not in STAGES:
            raise ValueError(f"unknown stage {name!r}; expected one of {STAGES}")
        start = time.perf_counter()
        try:
            yield
        finally:
            self._current[name] = (time.perf_counter() - start) * 1000.0

    def record(self, name: str, ms: float) -> None:
        """Record a pre-measured stage duration (ms) in the current frame."""
        if name not in STAGES:
            raise ValueError(f"unknown stage {name!r}; expected one of {STAGES}")
        self._current[name] = ms


def _series(recorder: Recorder) -> dict[str, list[float]]:
    series: dict[str, list[float]] = {s: [] for s in STAGES}
    for frame in recorder.iterations:
        for stage, ms in frame.items():
            series[stage].append(ms)
    return series


@dataclass(frozen=True)
class StageStats:
    stage: str
    p50: float
    p95: float
    p99: float
    count: int


@dataclass(frozen=True)
class LatencyReport:
    per_stage: dict[str, StageStats]
    end_to_end_p50: float
    end_to_end_p95: float
    end_to_end_p99: float
    glue_p95: float
    frames: int

    @classmethod
    def from_recorder(cls, recorder: Recorder) -> LatencyReport:
        series = _series(recorder)
        per_stage = {
            s: StageStats(
                stage=s,
                p50=percentile(series[s], 50),
                p95=percentile(series[s], 95),
                p99=percentile(series[s], 99),
                count=len(series[s]),
            )
            for s in STAGES
        }
        e2e = [sum(frame.values()) for frame in recorder.iterations]
        glue = [sum(ms for st, ms in frame.items() if st in GLUE_STAGES) for frame in recorder.iterations]
        return cls(
            per_stage=per_stage,
            end_to_end_p50=percentile(e2e, 50),
            end_to_end_p95=percentile(e2e, 95),
            end_to_end_p99=percentile(e2e, 99),
            glue_p95=percentile(glue, 95),
            frames=len(recorder.iterations),
        )


@dataclass(frozen=True)
class Budget:
    """Latency budget. The end-to-end ceiling is the product's hard requirement."""

    end_to_end_p95_ms: float = 50.0
    glue_p95_ms: float = 5.0

    def violations(self, report: LatencyReport) -> list[str]:
        out: list[str] = []
        if report.end_to_end_p95 > self.end_to_end_p95_ms:
            out.append(f"end-to-end p95 {report.end_to_end_p95:.2f}ms > {self.end_to_end_p95_ms:.2f}ms")
        if report.glue_p95 > self.glue_p95_ms:
            out.append(f"glue p95 {report.glue_p95:.2f}ms > {self.glue_p95_ms:.2f}ms")
        return out
