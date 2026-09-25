# OBSERVABILITY — gestureOS

> Observability & operability snapshot. Tags: **FACT** / **INFERENCE** / **UNKNOWN**.

## Current state

**FACT** — The repo is a pre-alpha bootstrap with no running service, so there is no
deployed observability stack (no logging config, metrics exporter, tracing, or error
tracker wired in the code today). The only "observability" primitive that exists is the
**latency instrumentation**.

## Latency observability (implemented)

**FACT** — `gestureos/perf.py` + `benchmarks/latency.py` provide:
- Per-stage timing recorder over stages
  `capture | inference | landmark_to_gesture | resolve | dispatch | os_call`.
- Percentile reporting (**p50 / p95 / p99**) and a budget assertion.
- A **glue sub-budget (p95 < 5 ms)** enforced now on the no-op backend; the full
  end-to-end **p95 < 50 ms** budget activates once real frame fixtures land (plan Step 6a).
- Output rendered via `rich` (e.g. "budget OK (glue sub-budget…)").

This is the metric the product is judged on; it is exercised by `make bench` and by
`tests/test_perf.py` / `tests/test_benchmark.py`.

## Error handling / logging

**FACT** — `core/` raises typed `ValueError`s for invalid percentiles and unknown stages
(`gestureos/perf.py`). No structured logging or centralized error handling module exists
yet. The chrysa canon norm is **error-tracking → GitHub issues** and typed, contained,
observable failures (`standards/rules/observability.md`, `code-quality.md`) — **PLANNED**,
not yet wired.

## Planned (from the canon & plan)

- **INFERENCE** — When the pipeline and dashboard (plan Step 11, PyQt6) exist, live
  per-stage latency and mapping state become the primary operational signals.
- **UNKNOWN** — Concrete logging backend, Sentry/GitHub-issue error routing, and any
  runtime metrics export are undefined in the repo.

## Operational notes

**FACT**
- The app has no server mode; `make run` (`python -m gestureos`) prints the version stub.
- Container versioning is separated from the app per canon; only `Dockerfile.test` (a test
  image) exists today — no production image / compose file is present.
