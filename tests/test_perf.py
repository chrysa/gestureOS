"""Tests for the latency measurement primitives."""

from __future__ import annotations

import pytest

from gestureos.perf import (
    GLUE_STAGES,
    STAGES,
    Budget,
    LatencyReport,
    Recorder,
    percentile,
)


@pytest.mark.parametrize(
    ("values", "q", "expected"),
    [
        ([], 95, 0.0),
        ([5.0], 50, 5.0),
        ([1.0, 2.0, 3.0, 4.0], 50, 2.5),
        ([1.0, 2.0, 3.0, 4.0], 0, 1.0),
        ([1.0, 2.0, 3.0, 4.0], 100, 4.0),
    ],
)
def test_percentile(values: list[float], q: float, expected: float) -> None:
    assert percentile(values, q) == pytest.approx(expected)


def test_percentile_rejects_out_of_range() -> None:
    with pytest.raises(ValueError, match="q must be in"):
        percentile([1.0], 150)


def test_recorder_groups_stages_per_frame() -> None:
    rec = Recorder()
    for _ in range(3):
        with rec.frame():
            rec.record("capture", 10.0)
            rec.record("inference", 20.0)
    assert len(rec.iterations) == 3
    assert rec.iterations[0] == {"capture": 10.0, "inference": 20.0}


def test_recorder_rejects_unknown_stage() -> None:
    rec = Recorder()
    with rec.frame(), pytest.raises(ValueError, match="unknown stage"):
        rec.record("not_a_stage", 1.0)


def test_stage_context_manager_times() -> None:
    rec = Recorder()
    with rec.frame(), rec.stage("resolve"):
        pass
    assert "resolve" in rec.iterations[0]
    assert rec.iterations[0]["resolve"] >= 0.0


def test_report_end_to_end_is_sum_of_stages() -> None:
    rec = Recorder()
    with rec.frame():
        for stage in STAGES:
            rec.record(stage, 1.0)
    report = LatencyReport.from_recorder(rec)
    assert report.end_to_end_p50 == pytest.approx(float(len(STAGES)))
    assert report.glue_p95 == pytest.approx(float(len(GLUE_STAGES)))
    assert report.frames == 1


def test_budget_flags_violation() -> None:
    rec = Recorder()
    with rec.frame():
        for stage in STAGES:
            rec.record(stage, 100.0)  # 600 ms total -> way over
    report = LatencyReport.from_recorder(rec)
    violations = Budget().violations(report)
    assert any("end-to-end" in v for v in violations)
    assert any("glue" in v for v in violations)


def test_budget_passes_within_limits() -> None:
    rec = Recorder()
    with rec.frame():
        for stage in STAGES:
            rec.record(stage, 0.5)  # 3 ms total, glue 1.5 ms
    report = LatencyReport.from_recorder(rec)
    assert Budget().violations(report) == []
