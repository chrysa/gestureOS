"""Smoke test for the runnable latency harness on the no-op backend."""

from __future__ import annotations

from benchmarks.latency import main, run_noop
from gestureos.perf import Budget


def test_noop_run_within_glue_budget() -> None:
    report = run_noop(frames=50)
    assert report.frames == 50
    # capture/inference/os_call are not measured on the no-op backend.
    assert report.per_stage["capture"].p95 == 0.0
    assert report.per_stage["inference"].p95 == 0.0
    # glue stages did run.
    assert report.per_stage["resolve"].p95 > 0.0
    assert Budget().violations(report) == []


def test_harness_main_returns_zero() -> None:
    assert main() == 0
