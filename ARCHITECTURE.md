# ARCHITECTURE — gestureOS

> Root-level architecture overview. The layer design already lives in
> [`docs/architecture.md`](docs/architecture.md); this file is the top-level entry point
> and does not duplicate it. Binding rules are in [`DECISIONS.md`](DECISIONS.md).
> Tags: **FACT** / **INFERENCE** / **UNKNOWN**.

## 1. Design intent (Option A — "extract-after")

**FACT** — ~80% of the logic is modality- and OS-agnostic and lives in an internal
**`core/`** package. `core/` is the extraction target for a shared library, lifted only
when voiceOS becomes the second real consumer (rule of three). No shared lib is built
upfront. (`CLAUDE.md` lines 9–16; `DECISIONS.md` D-0002.)

## 2. Layers (as implemented today)

**FACT** — Present in the repo:

| Path | Role | Status |
| --- | --- | --- |
| `core/types.py` | `ActionId`, `ModalityId`, `Trigger`, `Profile` (opaque modality config) | Implemented |
| `core/events.py` | `PerceptionEvent[P]`, `ContextSnapshot`, `ActionRequest`, `ActionResult`, `ModalityPayload` marker | Implemented |
| `core/protocols.py` | `ModalityEngine`, `ContextProvider`, `CommandRegistry`, `ActionResolver`, `OSController`, `ProfileStore`, `CalibrationStore` (Protocols, no concrete classes) | Implemented |
| `core/bus.py` | asyncio pub/sub `Bus` (fan-out, bounded, newest-wins) + `FastPath` (synchronous inline dispatch for the hot loop) | Implemented |
| `gestureos/cli.py` | Click CLI — **version stub only** | Stub |
| `gestureos/perf.py` | latency measurement helpers (percentiles, per-stage recorder, budget) | Implemented |
| `benchmarks/latency.py` | latency harness driving the no-op backend | Implemented |

**FACT** — Declared but **not yet present** (target layout per `CLAUDE.md` lines 18–27 /
`docs/architecture.md`): `gestureos/modalities/` (gesture, eye), `gestureos/oscontrol/`
(per-OS backends), `gestureos/context/`, `gestureos/resolve/`, `gestureos/app/`
(composition root).

## 3. Data / event flow (target)

**FACT** — `PerceptionEvent → ContextSnapshot → ActionRequest → ActionResult`, i.e.
perception → context → resolution → action → OS control. `PerceptionEvent` is **generic
over a modality-owned `payload: P`** (bounded by `ModalityPayload`) so no modality-specific
type enters `core/`. (`core/events.py` docstrings; `docs/architecture.md` lines 33–35.)

## 4. The extraction invariant

**FACT** — `core/` must not import `gestureos`. Enforced two ways:
1. **import-linter** forbidden contract (`make imports` / CI; `pyproject.toml`
   `[tool.importlinter]`, `forbidden_modules = ["gestureos"]`).
2. **Two-fake-consumer contract test** (`tests/test_core_contract.py`): a gesture-fake and
   a voice-fake run the identical `event → context → resolve → dispatch` core path.
(`docs/architecture.md` lines 21–35; `AGENTS.md` lines 9–10.)

## 5. Latency architecture (D-0005)

**FACT** — Two dispatch paths. The asyncio `Bus` handles **fan-out** (context, dashboard,
logging) where small queueing latency is acceptable; it is bounded and newest-wins so a
slow consumer never stalls publishers. The **perception→action** chain bypasses the bus
via `FastPath` (direct synchronous inline dispatch) to protect the p95 < 50 ms budget — an
async queue hop per frame would add latency and jitter. (`DECISIONS.md` D-0005;
`docs/architecture.md` lines 37–43.)

## 6. Perception stack (planned)

**FACT** — MediaPipe **Tasks API** only (`HandLandmarker` / `FaceLandmarker` with a
downloaded `.task` model); the legacy `mediapipe.solutions` API is removed and must not be
used. `opencv-python-headless` is used so CI imports cleanly without an X server.
(`DECISIONS.md` D-0003; `CLAUDE.md` line 31.)

## 7. Cross-OS control (planned)

**FACT** — One `OSController` protocol (`core/protocols.py`) with backends for Linux,
Windows (`pyautogui` / `pywin32` / `pygetwindow`, installed via platform markers,
`pyproject.toml` `[project.optional-dependencies].windows`), and a no-op/recording backend
for headless CI. **UNKNOWN** — the concrete Linux backend library choice is not fixed in
code yet (README phrasing only).

## 8. Related documents

- Layer detail: [`docs/architecture.md`](docs/architecture.md)
- Decisions: [`DECISIONS.md`](DECISIONS.md)
- Build plan: [`plans/gestureos-construction.md`](plans/gestureos-construction.md)
- Constraints: [`CONSTRAINTS.md`](CONSTRAINTS.md) · Technical requirements: [`TRD.md`](TRD.md)
