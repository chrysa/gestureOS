# ROADMAP — gestureOS

> Transcribed from the authoritative plan
> [`plans/gestureos-construction.md`](plans/gestureos-construction.md) and `CLAUDE.md`.
> Status marks are **FACT** where the plan/repo states them; otherwise the step is
> **PLANNED**. One step ≈ one PR.

## Serial spine (from `CLAUDE.md` lines 39–41)

Step 0 (dep spike ✅) → 1 (bootstrap) → 1b (latency harness) → 2 (core/) → 5b (app) →
6a/6b/6c (gesture MVP) → 7/7b (multiscreen) → 8 (eye) → 9 (media) → 10 (contextual AI) →
11b (packaging) → 12 (core/ extraction audit → unblocks voiceOS).

## Steps

| Step | Title | Status |
| --- | --- | --- |
| 0 | Dependency spike: vision stack on Python 3.14 | ✅ DONE 2026-06-04 (`plans/…` L73) |
| 1 | Repo bootstrap (`chrysa/gestureOS`) | DONE (repo scaffolded; CHANGELOG "Repository bootstrap") |
| 1b | Latency budget definition + harness skeleton | DONE (`gestureos/perf.py`, `benchmarks/latency.py`) |
| 2 | Core package skeleton: protocols + pub/sub bus | DONE (`core/*.py`, contract test) |
| 3 | OS Control Layer (cross-OS backends) | PLANNED (parallel with 4, 5) |
| 4 | Command Registry + Action Resolver + Profiles | PLANNED (parallel with 3, 5) |
| 5 | Context Engine (protocol-only) | PLANNED (parallel with 3, 4) |
| 5b | App composition root + CLI + runtime foundations | PLANNED |
| 6a | Vision Core + MediaPipe Hands stream (Phase 1) | PLANNED — unblocks real latency fixtures |
| 6b | Cursor-move gesture end-to-end, 1 screen (Phase 1) | PLANNED |
| 6c | Click / scroll / drag gestures (Phase 1) | PLANNED |
| 7 | MultiScreen (4 screens, spatial mapping) (Phase 2) | PLANNED |
| 7b | Calibration persistence (`CalibrationStore`) | PLANNED (prereq for Step 8) |
| 8 | Eye Tracking Modality (Phase 3) | PLANNED |
| 9 | Media Control (Phase 4) | PLANNED |
| 10 | Contextual AI (Phase 5) | PLANNED |
| 11 | PyQt6 Dashboard | PLANNED (shell after Step 2; mapping panel after Step 4) |
| 11b | Packaging / distribution | PLANNED |
| 12 | `core/` extraction-readiness audit → unblocks voiceOS | PLANNED |

> **Note:** Steps 1/1b/2 are marked DONE here by **INFERENCE** from the code present
> (matching artefacts exist and pass the described contracts); the plan file's own explicit
> ✅ mark is on Step 0. Confirm exact step-completion status against merged PRs if precise
> tracking is needed.

## Invariants re-verified after every step

**FACT** (`plans/…` §"Invariants", L375): the extraction invariant (no modality type in
`core/`), the latency budget, and the two-fake-consumer contract are checked after each
step. Open decisions deferred to execution are listed at the end of the plan (L383).
