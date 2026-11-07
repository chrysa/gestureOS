# Architecture — gestureOS

> Grounded in the repository as it stands. Where docs and manifests disagreed, the
> manifests (`pyproject.toml`, `Makefile`, source) were trusted. `pyproject.toml`
> declares the package name as `gestureos` (README title: "gestureOS").

## Purpose

gestureOS turns any webcam into a hands-free input device: move the cursor, click,
scroll, drag and control media from camera-driven gestures, across multi-screen setups.
It is the **leader** of a re-separated pair with voiceOS (its voice-driven twin), and is
designed so a modality-agnostic `core/` can later be extracted into a library shared by
both (DECISIONS.md D-0002, enforced by import-linter).

Current state (per README and source): only the **foundation** is implemented — typed
protocols, event/value types, the pub/sub bus + synchronous latency fast-path, and the
latency harness. The webcam perception and OS-control pipeline are **not implemented
yet**. The CLI is a bootstrap stub that only prints its version.

## Stack

- Language: Python (`requires-python` in `pyproject.toml`; classifiers list Python 3.14; Pre-Alpha).
- Build backend: `hatchling`.
- Runtime deps: `mediapipe`, `opencv-python-headless`, `numpy`, `pydantic`,
  `pydantic-settings`, `click`, `rich`, `screeninfo`.
- Windows-only OS-control extra (`[windows]`, platform-marked): `pyautogui`, `pywin32`, `pygetwindow`.
- Dev deps (`[dev]`): `pytest`, `pytest-asyncio`, `pytest-cov`, `pytest-mock`, `ruff`,
  `mypy`, `pre-commit`, `import-linter`.
- Tooling: Ruff (lint + format), mypy, import-linter, pytest (cov gate `--cov-fail-under=80`).

## Layout

- `core/` — modality-agnostic foundation (extraction target; must not import `gestureos`).
  - `types.py` — value types: `ActionId`, `ModalityId`, `Trigger`, `Profile`, `ModalityConfig` protocol.
  - `events.py` — event schemas: `PerceptionEvent[P]`, `ContextSnapshot`, `ActionRequest`, `ActionResult`.
  - `protocols.py` — structural interfaces: `ModalityEngine`, `ContextProvider`, `CommandRegistry`, `ActionResolver`, `OSController`, `ProfileStore`.
  - `bus.py` — async pub/sub `Bus` (bounded, newest-wins backpressure) + synchronous `FastPath` for the hot loop.
- `gestureos/` — the application package.
  - `cli.py` — Click/Rich CLI (bootstrap stub); `__main__.py` entry point; `perf.py` latency primitives (percentiles, per-stage timing, `Budget`).
- `benchmarks/` — `latency.py` runnable harness (`fixtures/` for recorded frames, target Step 6a).
- `tests/` — pytest suite (contract, perf, smoke, benchmark) + `fakes.py`.
- `docs/`, `plans/`, `scripts/`, `standards/`, `graphify-out/` — docs, construction plan, tooling, standards, graph output.

## Entrypoints

- Console script: `gestureos = "gestureos.cli:main"` (`pyproject.toml`).
- `python -m gestureos` → `gestureos/__main__.py` → `gestureos.cli:main`.
- `make run` → `python -m gestureos`.
- `python -m benchmarks.latency` (`make bench`) — latency harness.
- Today all CLI does is print the version / help (stub).

## Data & external dependencies

- No database, no network services in the repo.
- Perception via camera + MediaPipe/OpenCV (planned, not yet wired).
- OS control abstracted behind the `OSController` protocol; Windows backend deps are
  platform-marked; a no-op backend is used until real backends land.
- `screeninfo` for multi-screen enumeration.
- Latency contract: end-to-end p95 < 50 ms (glue sub-budget < 5 ms today).

## Build & test

Tests and linters are meant to run in Docker (`Dockerfile.test`, mirrors CI) or via
pre-commit — not directly on the host (MediaPipe needs system libs baked into the image).
Real commands (`Makefile`):

```bash
make dev           # editable install with [dev] extras + pre-commit hooks
make test          # pytest tests/ -v
make test-cov      # pytest with coverage
make docker-test   # build + run the test suite in Docker (canonical)
make lint          # ruff check core gestureos benchmarks tests
make format        # ruff format ...
make typecheck     # mypy core gestureos tests benchmarks
make imports       # lint-imports (core/ extraction invariant)
make bench         # python -m benchmarks.latency
make build         # python -m build (wheel)
make ci            # lint + typecheck + test
```
