# GestureOS — Construction Blueprint

> **Objective**: Build GestureOS — a Python 3.14 desktop-control app (camera-driven gestures + eye tracking) as the **leader** of a re-separated gestureOS / voiceOS pair.
>
> **Architecture decision (locked, 2026-06-04)**: Option A *extract-after*. The 4 core modules (Context Engine, Action Resolver, Command Registry, OS Control Layer) live in an internal `core/` package designed for later extraction into a shared lib when VoiceOS begins. Do **not** build the shared lib upfront — extract it when VoiceOS is the second real consumer (rule of three).
>
> **Hard constraint**: perception → action latency budget **< 50 ms** (real pipeline, p95 — see Step 1b benchmark definition).
>
> **Conventions**: English docs/commits/PRs. Docker-only tests/lint (never run pytest/ruff on host). pre-commit + SonarCloud (`chrysa_gestureos`). GitVersion releases.
>
> **Notion**: [GestureOS portfolio entry](https://www.notion.so/37559293e35e81309cf4d45085baafbe) · [VoiceOS twin](https://www.notion.so/37559293e35e81848692e45f187d6395) · [ChrysaOS design ref (archived)](https://www.notion.so/35659293e35e81f7b7abd6dcfcaafc33)
>
> *Hardened 2026-06-04 after adversarial review (findings C1–C2, I1–I7, M1–M6 addressed).*

---

## Pre-flight (verified during research phase)

- `chrysa/gestureOS` repo **does not exist yet** → Step 1 bootstraps it, **gated by Step 0** (dependency spike).
- Template reference: `chrysa/lifeos` (Python repo with Makefile, `pyproject.toml`, `Dockerfile.test`, `.pre-commit-config.yaml`, `sonar-project.properties`, `GitVersion.yml`, `cliff.toml`, `.github/`).
- ⚠️ **ruff py314 formatter bug** (org-wide, ~20 chrysa repos): `ruff format` + `target-version = py314` strips except-clause parens → invalid Python. **Pin `target-version = "py313"`** in `pyproject.toml` even though runtime is 3.14. Track upstream fix to revert later.
- ⚠️ MediaPipe + OpenCV need a camera device + recent-Python wheels; CI runs headless. See **Step 0** — this can force the runtime version decision *before* bootstrap.
- ⚠️ `pyautogui`/`pywin32` are Windows-centric; on Linux the OS Control Layer uses `ydotool`/`wmctrl`/`xdotool`. `ydotool` needs `uinput` access (permission footgun — document it). Keep OS Control behind a protocol with per-OS backends + a **no-op/recording backend** for headless CI and overhead isolation.

---

## Dependency graph

```
Step 0 (dep spike: mediapipe/opencv on target Python)   ◀── may change runtime version
   │
Step 1 (repo bootstrap)
   │
Step 1b (latency budget definition + harness skeleton)
   │
Step 2 (core/ skeleton: protocols + pub/sub + 2 fake consumers + import-linter)   ◀── strongest model
   ├──────────────┬───────────────┬───────────────────────────┐
Step 3          Step 4          Step 5 (Context Engine,      Step 11 (dashboard shell
(OS Control)   (CmdReg+        codes to OSController         + calibration — after S2;
               ActionResolver  *protocol*, fake backend;     mapping panel needs S4)
               + Profiles)     real backend joins after S3)
   └──────────────┴───────────────┘
                  │
            Step 5b (App composition root + CLI + runtime foundations)
                  │
            Step 6a (Vision Core + MediaPipe Hands stream + recorded fixtures)
                  │
            Step 6b (cursor-move gesture end-to-end, 1 screen)
                  │
            Step 6c (click / scroll / drag gestures)
                  │
            Step 7 (MultiScreen 4)
                  │
            Step 7b (CalibrationStore persistence)   ◀── prereq for Step 8
                  │
            Step 8 (Eye Tracking)
                  │
            Step 9 (Media Control)
                  │
            Step 10 (Contextual AI)
                  │
            Step 11b (Packaging / distribution)
                  │
            Step 12 (core/ extraction-readiness audit)   ◀── unblocks VoiceOS
```

**Parallelizable**: Steps 3, 4, 5 after Step 2 freezes protocols — but **Step 5 codes only against the `OSController` protocol** (tests on fake backend); real active-window detection on real backends is a follow-up joining after Step 3. Step 11 (dashboard shell) runs alongside 3–8; its **mapping panel sub-task depends on Step 4**.

**Serial spine**: 0 → 1 → 1b → 2 → 5b → 6a → 6b → 6c → 7 → 7b → 8 → 9 → 10 → 11b → 12.

---

## Step 0 — Dependency spike: vision stack on target Python  *(blocks bootstrap)* — ✅ DONE 2026-06-04

**Context brief**: Before committing to Python 3.14, prove the critical deps install and import. MediaPipe wheels historically lag new Python releases — if there is no `mediapipe` wheel for 3.14, the runtime version is a decision that must be made *now*, not discovered at Step 6.

**Model**: default.

**Tasks**: In a throwaway Docker image, attempt `pip install mediapipe opencv-python` on Python 3.14, then 3.13 as fallback. Import both, run a trivial MediaPipe Hands inference on a bundled sample image. Record the working Python version.

**Result (verified in `python:3.14-slim`)**:
- `mediapipe==0.10.35` + `opencv-python-headless==4.13.0` + `numpy==2.4.6` install & import on **Python 3.14** → runtime pinned to 3.14.
- ⚠️ **Legacy `mediapipe.solutions` API is removed** in 0.10.35 (absent on 3.13 *and* 3.14). The vision layer (Step 6a/8) **must use the MediaPipe Tasks API** — `mediapipe.tasks.python.vision.HandLandmarker` / `FaceLandmarker` with a downloaded `.task` model asset — **not** `mp.solutions.hands.Hands`. Wherever this plan says "MediaPipe Hands", read "Tasks `HandLandmarker`".
- Headless CPU inference ≈ 17 ms on a 256×256 frame → headroom under the 50 ms budget (confirm on the real reference machine at 1b/6a).
- Required system libs (Dockerfile.test / CI): `libgl1 libglib2.0-0 libxcb1 libgles2 libegl1`.
- Recorded in `DECISIONS.md` (D-0003).

**Exit criteria**: ✅ Python 3.14 confirmed; Tasks API mandated; libs + versions documented.

**Rollback**: N/A (spike).

---

## Step 1 — Repo bootstrap (`chrysa/gestureOS`)

**Context brief**: Brand-new public repo following chrysa Python conventions. Mirror `chrysa/lifeos` layout. No app logic yet — only scaffolding that makes `make lint` / `make test` pass green on an empty package. Use the runtime version confirmed in Step 0.

**Model**: default.

**Tasks**:
- `gh auth switch -u chrysa`, then `gh repo create chrysa/gestureOS --public`. Init local, default branch `main`.
- `pyproject.toml`: package `gestureos`, runtime from Step 0, ruff + **`target-version = "py313"`**, pytest config, deps (opencv-python, mediapipe, pyautogui/pywin32 under Windows platform markers), dev deps (pytest, ruff, pytest-cov, **import-linter**).
- `Makefile` extending base-makefile: `setup`, `lint`, `test` (Docker), `scan`, `changelog`, `bench` (latency harness).
- `Dockerfile.test` (mirror lifeos). All tests/lint run here.
- `.pre-commit-config.yaml`, `.secrets.baseline`, `.yamllint`, `.editorconfig`, `.gitignore`.
- `sonar-project.properties` → key `chrysa_gestureos`. **Create the SonarCloud project + `SONAR_TOKEN` secret** (manual dashboard action — flag if blocked). Configure a **new-code-focused quality gate** so a near-empty MVP package doesn't red-gate the bootstrap PR (per recurring chrysa SonarCloud pain).
- `.github/workflows/`: CI (lint+test in Docker), secret-scan (reusable workflow), release (GitVersion). `checkout@v4` / `upload-artifact@v4`.
- `GitVersion.yml`, `cliff.toml`, `LICENSE`, `README.md`, `CLAUDE.md`, `AGENTS.md`, `CONTRIBUTING.md`, `DECISIONS.md` (record Option A extract-after + Step 0 runtime decision), `docs/manual-smoke.md` (human verification checklist referenced by later steps).
- Empty `gestureos/__init__.py` + one trivial passing test.

**Verification**: `make lint` + `make test` green in Docker. CI green on first PR. `gh repo view chrysa/gestureOS`.

**Exit criteria**: Repo exists, CI green, SonarCloud resolves (no 404), gate clearable. This blueprint moved into the repo at `plans/`.

**Rollback**: `gh repo delete` (external state — note SonarCloud project + secret also need manual cleanup).

---

## Step 1b — Latency budget definition + harness skeleton

**Context brief**: Define what "< 50 ms" *means* and how it's measured, before any modality exists — so the number is honest from day one. A no-op-backend timing only measures glue code; the real cost is MediaPipe inference + capture.

**Model**: default.

**Tasks**:
- `benchmarks/latency.py`: measures **p50/p95/p99** (not mean) over a committed set of **recorded frames** pushed through the real pipeline, on a declared reference machine (documented in `docs/manual-smoke.md`).
- **Per-stage budget breakdown** asserted separately: `capture | inference | landmark→gesture | resolve | dispatch | OS-call`. End-to-end p95 < 50 ms; glue-only (no-op backend) sub-budget < 5 ms.
- Recorded-frame fixtures placeholder (populated in Step 6a).
- `make bench` wired.

**Verification**: Harness runs on the no-op backend now (glue sub-budget), ready to consume real frames at Step 6a.

**Exit criteria**: Budget is per-stage + percentile-based + reproducible; documented.

**Rollback**: Revert PR.

---

## Step 2 — Core package skeleton: protocols + pub/sub bus

**Context brief**: The **most important step** — it freezes the abstractions VoiceOS will reuse. Define `core/` module boundaries, typed `Protocol`s, an asyncio pub/sub bus, and modality-agnostic event schemas. **No modality, no real OS calls.** Prove extractability from day one by wiring **two fake consumers (gesture-fake AND voice-fake)** through the same path, and enforce import direction with **import-linter** — not grep.

**Model**: **strongest** (Opus) — interface design determines extraction cost.

**Tasks**:
- `core/bus.py`: asyncio pub/sub (topic → async subscribers), backpressure-aware, typed. Reserve the bus for fan-out (context, dashboard, logging); design a **direct synchronous fast-path** option for the perception→action chain (latency, see M1) and document the choice.
- `core/events.py`: dataclasses — `PerceptionEvent` (modality-agnostic; **no `payload: Any` dumping ground** — use a typed, modality-owned config registered into core, not raw gesture fields), `ContextSnapshot`, `ActionRequest`, `ActionResult`.
- `core/protocols.py`: `Protocol`s — `ContextProvider`, `ActionResolver`, `CommandRegistry`, `OSController`, `ModalityEngine`, `ProfileStore`, **`CalibrationStore`**. A `ModalityEngine` emits `PerceptionEvent`s — gesture/voice/eye implement it identically.
- `core/types.py`: `ActionId`, `Trigger` (gesture | voice_intent | gaze_target | composite), `Profile` — **`Profile` holds only modality-agnostic structure** (`dict[modality_id, ModalityConfig]` opaque to core); gesture-specific config (pinch threshold, dead-zone) is defined in the gesture module and registered, never in core.
- Stub/fake implementations; unit tests of the bus and a **two-consumer** contract round-trip (gesture-fake + voice-fake → context → resolve → fake OS controller) proving the path is modality-neutral.
- **import-linter** contract: forbid `core` → `gestureos.modalities` (and any modality package). Runs in CI from this step on.
- `docs/architecture.md` + `DECISIONS.md`: "core/ is extraction-target; no modality-specific types leak into core/."

**Verification**: import-linter green. Two-fake-consumer round-trip test passes with zero modality-specific code in `core/`. `Profile`/`PerceptionEvent` carry no gesture fields.

**Exit criteria**: Interfaces frozen + reviewed; bus tested; extraction invariant enforced by import-linter + the two-consumer test.

**Rollback**: Revert PR; Steps 3–5 not yet started.

---

## Step 3 — OS Control Layer (cross-OS backends)  *(parallel with 4, 5)*

**Context brief**: Implement `OSController` with per-OS backends behind a factory. Linux: `ydotool`/`wmctrl`/`xdotool`. Windows: `pywin32`/`pyautogui`/`pygetwindow`. Plus a **no-op/recording backend** for latency tests + headless CI.

**Model**: default.

**Tasks**: cursor move (absolute/relative), click, scroll, drag, window focus/list, screen enumeration via `screeninfo`. Platform markers; never import `pywin32` on Linux. Latency-instrument each call. Document `ydotool` uinput permission setup.

**Verification**: Unit tests against no-op backend (CI-safe). Linux smoke recorded in `docs/manual-smoke.md`.

**Exit criteria**: All `OSController` methods implemented + tested on no-op + one real backend.

**Rollback**: Revert PR; core/ contract unaffected.

---

## Step 4 — Command Registry + Action Resolver + Profiles  *(parallel with 3, 5)*

**Context brief**: Unified registry (`action_id` → triggers + allowed context + per-modality thresholds + profile scoping) + resolver (target app, multimodal priority, sync vs deferred). Profile Manager loads TOML profiles (Travail / Présentation / Média), modality config held opaquely per Step 2.

**Model**: default.

**Tasks**: registry CRUD + conflict detection; resolver priority policy per profile; TOML profile loader using the modality-agnostic `Profile` schema; import/export config. `voice_intent` trigger is a first-class citizen now (dormant).

**Verification**: Test: same `action_id` triggered by a fake gesture and a fake voice intent resolves identically under a profile.

**Exit criteria**: Registry + resolver + profiles tested; voice-trigger path proven dormant-but-ready.

**Rollback**: Revert PR.

---

## Step 5 — Context Engine  *(parallel with 3, 4 — protocol-only)*

**Context brief**: Implement `ContextProvider`: publishes normalized `ContextSnapshot` (active app/process/window class, current screen, user mode, modality states). **Codes against the `OSController` protocol only** (Step 2), tested with the fake backend — real active-window detection on real backends is a follow-up joining after Step 3.

**Model**: default.

**Tasks**: window/screen detection via the `OSController` protocol; user-mode tracking; debounced publishing.

**Verification**: Tests with fake OS backend assert correct snapshots on simulated focus changes.

**Exit criteria**: Context snapshots flowing; consumed by resolver in an integration test.

**Rollback**: Revert PR.

---

## Step 5b — App composition root + CLI + runtime foundations

**Context brief**: Turn components into a **runnable app**. This is the missing piece between "tests pass" and "a thing you can launch." Owns the asyncio loop, dependency wiring, lifecycle, and the cross-cutting concerns nothing else homes (logging, app-config, error/degradation policy).

**Model**: default.

**Tasks**:
- `gestureos/app.py`: composition root — builds bus + context + registry + resolver + OS backend + (later) modality engines; owns the event loop; startup/shutdown ordering; signal handling; graceful shutdown.
- `gestureos/__main__.py` + `[project.scripts]` console entry (`gestureos`).
- **App config** schema + loader (Pydantic): camera index, MediaPipe model paths/complexity, OS backend selection, log level, calibration file location, latency thresholds. Separate from TOML *profiles*.
- **Logging/observability**: structured logging setup; per-stage latency timings surfaced to logs + a metrics hook the dashboard reads.
- **Error/degradation policy** + taxonomy: `CaptureLost`, `BackendUnavailable`, dropped-frame handling, action-failure surfacing. A real-time control app must degrade, not crash.

**Verification**: `python -m gestureos --help` works; app boots with no modality and shuts down cleanly; config + logging covered by tests; injected failures degrade per policy.

**Exit criteria**: Headless app runs end-to-end (no modality), clean lifecycle, config-driven, observable.

**Rollback**: Revert PR; components remain individually tested.

---

## Step 6a — Vision Core + MediaPipe Hands stream  *(Phase 1)*

**Context brief**: Camera acquisition behind an injectable `FrameSource` protocol (live + recorded-frames fake), MediaPipe Hands landmark stream onto the pipeline. **No gestures yet** — just frames → landmarks, plus the recorded-frame fixtures that feed the latency harness.

**Model**: default.

**Tasks**: `FrameSource` protocol (live OpenCV capture + recorded-frames fake); MediaPipe Hands integration; commit the recorded-frame fixture set; populate `benchmarks/latency.py` with the real inference path; measure per-stage p50/p95/p99.

**Verification**: Recorded-frame tests (no live camera in CI). Latency harness reports real per-stage numbers; inference stage characterized on the reference machine.

**Exit criteria**: Landmark stream flows from recorded + live frames; real latency numbers exist (even if tuning is pending).

**Rollback**: Revert PR.

---

## Step 6b — Cursor-move gesture end-to-end (1 screen)  *(Phase 1)*

**Context brief**: First full perception→action loop: index-finger landmark → cursor move, through the real spine (modality → context → resolver → OS Control), 1 screen. Validates the architecture and the latency budget on a real action.

**Model**: default.

**Tasks**: index-tracking gesture detection with smoothing/dead-zone; emit `PerceptionEvent`; wire through resolver → OS Control; assert end-to-end p95 < 50 ms on the reference machine via `make bench`.

**Verification**: Recorded-frame unit tests; latency p95 < 50 ms logged in PR; real-webcam smoke in `docs/manual-smoke.md`.

**Exit criteria**: Gesture moves the cursor end-to-end within budget on 1 screen.

**Rollback**: Revert PR; 6a stream intact.

---

## Step 6c — Click / scroll / drag gestures  *(Phase 1)*

**Context brief**: Remaining MVP gestures on top of 6b: click (thumb/index pinch), scroll (two fingers), drag. Thresholds, debounce, dead-zones per gesture.

**Model**: default.

**Tasks**: implement the three gestures; per-gesture thresholds in the gesture module's modality config (registered, not in core); conflict avoidance with cursor-move.

**Verification**: Recorded-frame tests per gesture; latency still within budget; webcam smoke.

**Exit criteria**: cursor/click/scroll/drag all work on 1–2 screens within budget.

**Rollback**: Revert PR; 6b cursor path intact.

---

## Step 7 — MultiScreen (4 screens, spatial mapping)  *(Phase 2)*

**Context brief**: Extend to 1→4 screens, mixed resolutions/orientations, free layout. Virtual-coordinate mapping + inter-screen transitions.

**Model**: default.
**Tasks**: topology from `screeninfo`; virtual coordinate space; transition smoothing; per-screen calibration **data model** (persistence in Step 7b).
**Verification**: Tests with synthetic multi-monitor topologies (mocked `screeninfo`); 2-monitor smoke.
**Exit criteria**: Cursor crosses screens correctly across ≥2 real + synthetic 4-screen topologies.
**Rollback**: Revert PR; single-screen path intact.

---

## Step 7b — Calibration persistence (`CalibrationStore`)  *(prereq for Step 8)*

**Context brief**: Implement the `CalibrationStore` protocol from Step 2. Gaze calibration is expensive to redo each launch — it must persist and survive monitor topology changes.

**Model**: default.
**Tasks**: versioned file format keyed by monitor identity; load-at-startup in the composition root; **invalidation when topology changes** (tie-in with Step 7); migration on schema version bump.
**Verification**: Tests: persist → reload → topology-change-invalidation. Round-trips for screen + (future) gaze calibration.
**Exit criteria**: Calibration survives restarts and invalidates correctly on layout change.
**Rollback**: Revert PR; calibration falls back to in-session only.

---

## Step 8 — Eye Tracking Modality  *(Phase 3)*

**Context brief**: `Eye Modality Engine` (implements `ModalityEngine`) via MediaPipe FaceMesh + gaze estimation → looked-at-screen detection, window focus, contextual pre-selection. Uses `CalibrationStore` (Step 7b). First building block toward future multimodal fusion (kept dormant per extract-after).

**Model**: default.
**Tasks**: FaceMesh integration; gaze→screen calibration (9-point per screen, persisted); focus/pre-selection events on the bus.
**Verification**: Recorded-frame tests for gaze classification; calibration smoke in `docs/manual-smoke.md`.
**Exit criteria**: Gaze selects the active screen; pre-selection events published; calibration persists.
**Rollback**: Revert PR.

---

## Step 9 — Media Control  *(Phase 4)*

**Context brief**: Detect active media app (VLC, YouTube, Spotify, Netflix, local players); map actions (pause/play/volume/next/fullscreen). Each action wired through the registry so it already supports a future voice trigger.

**Model**: default.
**Tasks**: per-app detection via Context Engine; action mappings; ≥2 triggers per action where sensible (gesture now, voice slot reserved).
**Verification**: Tests with mocked active-app context; VLC + YouTube smoke.
**Exit criteria**: Media actions fire for ≥2 real apps.
**Rollback**: Revert PR.

---

## Step 10 — Contextual AI  *(Phase 5)*

**Context brief**: Usage profiling, adaptive per-user thresholds, shortcut suggestions. Local-first; no cloud dependency (cloud NLU stays a VoiceOS concern).

**Model**: default (strongest if the adaptation model design is non-trivial).
**Tasks**: usage logging, threshold adaptation loop, suggestion surface.
**Verification**: Tests on synthetic usage logs; thresholds converge.
**Exit criteria**: Demonstrable adaptation on replayed usage.
**Rollback**: Revert PR; static thresholds remain default.

---

## Step 11 — PyQt6 Dashboard  *(shell after Step 2; mapping panel after Step 4)*

**Context brief**: Calibration (camera/gaze/screens/sensitivity), live tracking overlays, **Command Mapping Panel** (drag-and-drop triggers, conflict detection — needs Step 4), profile management, debug/logs (reads the Step 5b metrics hook). Consumes only public interfaces.

**Model**: default. Load the `ui-ux` skill (WCAG 2.1 AA, dark mode, i18n FR+EN) per project CLAUDE.md.
**Tasks**: PyQt6 shell + calibration flows (after Step 2); mapping panel bound to Command Registry (after Step 4); profile editor; live overlay reading bus events; log/metrics view.
**Verification**: UI smoke (manual, in `docs/manual-smoke.md`); logic-layer unit tests where feasible.
**Exit criteria**: Operator can calibrate, edit mappings, switch profiles from the GUI.
**Rollback**: Revert PR; app runs headless/CLI without dashboard.

---

## Step 11b — Packaging / distribution

**Context brief**: Produce a runnable artifact for an end user — currently the plan ships only a green-CI repo. Desktop app distribution differs sharply Windows vs Linux (MediaPipe wheels, camera permissions, `ydotool` uinput).

**Model**: default.
**Tasks**: decide pip-installable-with-documented-system-deps vs PyInstaller/briefcase bundle; per-OS install docs incl. camera + `uinput` permissions; define what a GitHub Release actually contains (tag + artifact).
**Verification**: Fresh-machine install following the docs reaches a running app (manual checklist).
**Exit criteria**: Documented, reproducible install path per target OS; release artifact defined.
**Rollback**: Revert PR; source-run still works.

---

## Step 12 — core/ extraction-readiness audit  *(unblocks VoiceOS)*

**Context brief**: Final gate before VoiceOS. Audit that `core/` is cleanly extractable. Produce the extraction plan but **do not extract yet** — that happens at VoiceOS kickoff.

**Model**: **strongest** (Opus) — adversarial check of the extraction invariant.
**Tasks**: import-linter contract review + dependency graph audit; API surface doc; `core/` standalone test run; confirm `Profile`/`PerceptionEvent` carry no modality fields; write `plans/core-extraction.md` for VoiceOS (target: standalone `chrysa-os-core` repo vs chrysa-lib module — decide here); tag a release.
**Verification**: `core/` test suite passes in isolation; import-linter proves no modality imports inside `core/`; two-consumer test still green.
**Exit criteria**: Green "extractable" verdict documented → VoiceOS can start.
**Rollback**: N/A (audit only; note the release tag is external state).

---

## Invariants (verified after every step)

1. `make lint` + `make test` green in Docker (never on host).
2. CI green; SonarCloud no 404; new-code quality gate respected.
3. **No modality-specific code in `core/`** — enforced by **import-linter** + the two-fake-consumer test (the extract-after guarantee).
4. Latency budget: end-to-end **p95 < 50 ms** on recorded frames through the **real** pipeline, per-stage breakdown, on the declared reference machine (from Step 6b onward). Glue-only sub-budget < 5 ms.
5. English-only in committed files; commits follow chrysa conventions; `gh auth switch -u chrysa` before any gh op.

## Open decisions deferred to execution

- Runtime Python version — set by Step 0 (3.14 if MediaPipe wheel exists, else 3.13).
- Primary MVP OS (Windows vs Linux) — recommend Linux first (dev host), Windows backend in parallel via the OS Control protocol.
- Bus vs synchronous fast-path on the perception→action chain — measure in Step 6b, decide (M1).
- Shared-lib home: standalone `chrysa-os-core` repo vs module in chrysa-lib — decide at Step 12.
- Wake word / cloud NLU — out of scope (VoiceOS concern).
