# REQUIREMENTS — gestureOS

> Requirement matrix. **Status** is one of: **IMPLEMENTED** (verifiable in code today),
> **PARTIAL**, **PLANNED** (declared, not built). Evidence pointers given. Product
> requirements are `REQ-PROD-00x`; technical `REQ-TECH-00x`.

## Product requirements

| ID | Requirement | Status | Evidence |
| --- | --- | --- | --- |
| REQ-PROD-001 | Move the cursor with hand gestures | PLANNED | `README.md` L30; plan Step 6b |
| REQ-PROD-002 | Click / scroll / drag with hand gestures | PLANNED | plan Step 6c |
| REQ-PROD-003 | Media control (play/pause…) via gesture | PLANNED | `README.md` L31; plan Step 9 |
| REQ-PROD-004 | Multi-screen spatial mapping across 1–4 screens | PLANNED | `README.md` L32; plan Step 7; `screeninfo` dep |
| REQ-PROD-005 | Gaze-based screen focus | PLANNED | `README.md` L33; plan Step 8 |
| REQ-PROD-006 | Cross-OS control (Linux + Windows) behind one protocol | PARTIAL | `OSController` protocol exists (`core/protocols.py`); no backend implemented; Windows deps declared |
| REQ-PROD-007 | Contextual AI | PLANNED | plan Step 10 |
| REQ-PROD-008 | Runnable CLI entry point | PARTIAL | `gestureos` prints version only (`gestureos/cli.py`); real composition root = plan Step 5b |
| REQ-PROD-009 | Works with a plain webcam, no special hardware | PLANNED | `README.md` L3–9 (pipeline unbuilt) |

## Technical requirements

| ID | Requirement | Status | Evidence |
| --- | --- | --- | --- |
| REQ-TECH-001 | Modality-agnostic `core/` (protocols, events, types, bus) | IMPLEMENTED | `core/*.py` |
| REQ-TECH-002 | `core/` must not import `gestureos` (extraction invariant) | IMPLEMENTED | `pyproject.toml` `[tool.importlinter]`; `make imports` |
| REQ-TECH-003 | Two-fake-consumer contract test (gesture + voice) | IMPLEMENTED | `tests/test_core_contract.py` |
| REQ-TECH-004 | `PerceptionEvent` generic over modality-owned payload | IMPLEMENTED | `core/events.py` |
| REQ-TECH-005 | FastPath (synchronous) for perception→action hot loop | IMPLEMENTED | `core/bus.py`; D-0005 |
| REQ-TECH-006 | asyncio Bus for fan-out, bounded + newest-wins | IMPLEMENTED | `core/bus.py` |
| REQ-TECH-007 | Latency harness: per-stage p50/p95/p99, glue sub-budget < 5 ms | IMPLEMENTED | `benchmarks/latency.py`, `gestureos/perf.py`, `tests/test_perf.py`, `tests/test_benchmark.py` |
| REQ-TECH-008 | End-to-end perception→action p95 < 50 ms on real frames | PLANNED | budget defined; real fixtures = plan Step 6a (`benchmarks/fixtures/README.md`) |
| REQ-TECH-009 | Python 3.14 runtime | IMPLEMENTED | `pyproject.toml`; D-0003 |
| REQ-TECH-010 | MediaPipe Tasks API only (no legacy `solutions`) | PLANNED | rule set (D-0003); no vision code yet |
| REQ-TECH-011 | Tests/lint run in Docker or pre-commit, not host | IMPLEMENTED | `Dockerfile.test`, `make docker-test`; see contradiction in `TRD.md` §4 |
| REQ-TECH-012 | Coverage gate ≥ 80% | IMPLEMENTED | `pyproject.toml` `--cov-fail-under=80` |
| REQ-TECH-013 | CI runs tests + sonar; lint at release | IMPLEMENTED | `.github/workflows/ci.yml`, `release.yml`, `sonar.yml` |
| REQ-TECH-014 | Secret scanning gate (CI + pre-commit) | IMPLEMENTED | `.github/workflows/secret-scan.yml`; `.pre-commit-config.yaml` |
| REQ-TECH-015 | Generated context files (handover, ai-instructions, context-map, llms-full) | IMPLEMENTED | `scripts/gen_context_files.py`; generated files at root |

## Notes

- "IMPLEMENTED" here means the mechanism/scaffold is present and testable in the repo, not
  that the end product feature works. Product features (REQ-PROD-*) are almost all PLANNED
  because the perception→OS pipeline is not built (see [`PRD.md`](PRD.md) §3).
