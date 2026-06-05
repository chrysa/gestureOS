"""Runnable latency harness — `make bench` / `python -m benchmarks.latency`.

Measures p50/p95/p99 per stage and end-to-end over a set of frames pushed through
the pipeline, and asserts the budget (gestureos.perf.Budget).

Today there is no real pipeline yet (Step 2+), so this runs a **no-op backend**: it
only exercises glue stages and asserts the glue sub-budget (< 5 ms p95). The capture
and inference stages are recorded as 0 until real recorded frames land in Step 6a
(``benchmarks/fixtures/``), at which point this same harness measures the real
end-to-end p95 against the 50 ms ceiling.
"""

from __future__ import annotations

import sys
import time

from rich.console import Console
from rich.table import Table

from gestureos.perf import GLUE_STAGES, STAGES, Budget, LatencyReport, Recorder

console = Console()

# No-op backend: how many synthetic frames to push through the glue path.
DEFAULT_FRAMES = 500


def _spin(microseconds: float) -> None:
    """Busy-wait ~microseconds to simulate trivial glue work deterministically."""
    end = time.perf_counter() + microseconds / 1_000_000.0
    while time.perf_counter() < end:
        pass


def run_noop(frames: int = DEFAULT_FRAMES) -> LatencyReport:
    """Push synthetic frames through glue-only stages (no model, no real OS call)."""
    rec = Recorder()
    for _ in range(frames):
        with rec.frame():
            # capture / inference / os_call are device/model-bound -> 0 on no-op backend.
            rec.record("capture", 0.0)
            rec.record("inference", 0.0)
            rec.record("os_call", 0.0)
            for stage in (s for s in STAGES if s in GLUE_STAGES):
                with rec.stage(stage):
                    _spin(50)  # ~0.05 ms of representative glue work
    return LatencyReport.from_recorder(rec)


def render(report: LatencyReport, budget: Budget) -> None:
    table = Table(title=f"Latency — {report.frames} frames (no-op backend)")
    table.add_column("stage")
    table.add_column("p50 ms", justify="right")
    table.add_column("p95 ms", justify="right")
    table.add_column("p99 ms", justify="right")
    for stage in STAGES:
        st = report.per_stage[stage]
        table.add_row(stage, f"{st.p50:.3f}", f"{st.p95:.3f}", f"{st.p99:.3f}")
    table.add_section()
    table.add_row(
        "END-TO-END",
        f"{report.end_to_end_p50:.3f}",
        f"{report.end_to_end_p95:.3f}",
        f"{report.end_to_end_p99:.3f}",
    )
    console.print(table)
    console.print(
        f"glue p95 = {report.glue_p95:.3f} ms (budget {budget.glue_p95_ms:.1f} ms) | "
        f"end-to-end budget {budget.end_to_end_p95_ms:.1f} ms"
    )


def main() -> int:
    budget = Budget()
    report = run_noop()
    render(report, budget)
    violations = budget.violations(report)
    if violations:
        console.print("[red]BUDGET VIOLATED:[/red] " + "; ".join(violations))
        return 1
    console.print("[green]budget OK[/green] (glue sub-budget; real end-to-end pending Step 6a fixtures)")
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
