# Recorded frame fixtures

Placeholder. Populated in **Step 6a** (Vision Core) with a small, committed set of
recorded camera frames used to drive the **real** pipeline through `make bench`.

Until then the latency harness (`benchmarks/latency.py`) runs on the **no-op backend**
and only asserts the glue sub-budget (< 5 ms p95). Once real frames live here, the same
harness measures the real end-to-end p95 against the 50 ms ceiling, per stage
(`capture | inference | landmark_to_gesture | resolve | dispatch | os_call`).

Raw frame blobs (`*.raw`) are git-ignored; commit only compact encoded fixtures.
