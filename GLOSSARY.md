# GLOSSARY — gestureOS

> Terms used across the codebase and docs. Definitions are grounded in the repo
> (`core/`, `docs/architecture.md`, `DECISIONS.md`, `CLAUDE.md`).

| Term | Meaning |
| --- | --- |
| **gestureOS** | Hands-free desktop control from a webcam (gesture + gaze); leader of the gestureOS/voiceOS pair. |
| **voiceOS** | Voice-driven twin project; the second intended consumer of the extracted `core/`. |
| **`core/`** | The modality- and OS-agnostic foundation (protocols, events, types, bus). The extraction target for a future shared library. |
| **Modality** | An input channel (gesture, eye/gaze, later voice) that implements `ModalityEngine` and emits `PerceptionEvent`s. |
| **Option A / "extract-after"** | The decision (D-0002) to build `core/` inside gestureOS first and extract it only when voiceOS arrives (rule of three). |
| **Extraction invariant** | The rule that no modality-specific (or OS-specific) type may leak into `core/`; enforced by import-linter + the two-fake-consumer test. |
| **Two-fake-consumer test** | `tests/test_core_contract.py` — runs a gesture-fake and a voice-fake through the identical core path to prove `core/` is modality-agnostic. |
| **`ModalityEngine`** | Protocol producing a stream of perception events (gesture/voice/eye implement it identically). |
| **`ContextProvider`** | Protocol supplying the current desktop `ContextSnapshot`. |
| **`CommandRegistry`** | Protocol mapping triggers → action ids within a context/profile scope. |
| **`ActionResolver`** | Protocol turning a perception event + context into an `ActionRequest` (or nothing). |
| **`OSController`** | Protocol performing OS-level effects (move/click/scroll/drag/media); backends: Linux, Windows, no-op/recording. |
| **`ProfileStore` / `CalibrationStore`** | Protocols for loading named profiles and persisting per-setup calibration (e.g. screen mapping). |
| **`PerceptionEvent[P]`** | A single perception, generic over a modality-owned `payload: P` (bounded by `ModalityPayload`), so `core/` stays type-safe and agnostic. |
| **`ModalityPayload`** | Marker protocol for a modality's typed payload; core never reads its fields. |
| **`ContextSnapshot`** | Modality-agnostic view of the desktop at a point in time. |
| **`ActionRequest` / `ActionResult`** | A resolved request to act, and the outcome of dispatching it. |
| **`Trigger`** | A named trigger of a given kind, owned by a modality; opaque to core, which only routes it. |
| **`Profile`** | A named profile holding modality configs opaquely, keyed by `ModalityId`. |
| **`Bus`** | asyncio pub/sub for **fan-out** (context, dashboard, logging); bounded, newest-wins backpressure. |
| **`FastPath`** | Direct synchronous inline dispatch for the perception→action hot loop (no queue hop), protecting the latency budget (D-0005). |
| **Latency budget** | perception→action **p95 < 50 ms**, measured per stage; "law". |
| **Glue sub-budget** | Interim harness check (p95 < 5 ms) on the no-op backend until real frame fixtures exist (Step 6a). |
| **Stages** | `capture · inference · landmark_to_gesture · resolve · dispatch · os_call`. |
| **MediaPipe Tasks API** | The only allowed MediaPipe API (`HandLandmarker`/`FaceLandmarker` + `.task` asset); legacy `solutions` removed (D-0003). |
| **chrysa canon** | The shared-standards source of truth; managed blocks in `CLAUDE.md`/`AGENTS.md` come from `distribute-standards.sh`. |
| **Context files** | Generated `handover.md`, `ai-instructions.md`, `context-map.json`, `llms-full.txt` (regenerate, don't hand-edit). |
