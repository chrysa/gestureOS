# PRD — gestureOS

> Product Requirements Document. Facts are tagged **FACT** (verifiable in-repo),
> **INFERENCE** (reasoned from evidence), **UNKNOWN** (not determinable from the repo),
> **PROPOSAL** (suggestion, not yet decided). Evidence pointers are given inline.

## 1. Problem & vision

**FACT** — gestureOS turns any webcam into a hands-free desktop input device: move the
cursor, click, scroll, drag, and control media using hand gestures and gaze, across up to
four screens, with no special hardware or wearables. (`README.md` lines 3–4, 8–9;
`docs/reference/github-inspiration.md`.)

**FACT** — It is the **leader** of a re-separated pair; [voiceOS](https://github.com/chrysa/voiceOS)
is the voice-driven twin. Both are designed to build on the same extractable `core/`.
(`README.md` lines 39–40; `CLAUDE.md` line 7; `DECISIONS.md` D-0002.)

## 2. Target users

**FACT** — People who want or need to drive a desktop without a mouse: accessibility
users, hands-busy workflows, multi-screen setups, and anyone building on a low-latency
perception→action foundation. (`README.md` lines 13–14.)

## 3. Current status

**FACT** — **Pre-alpha / bootstrap.** Only the `core/` foundation (typed protocols, event
types, pub/sub bus + latency fast-path) and the latency harness ship today. The webcam
perception and OS-control pipeline is **not implemented yet**; the CLI is a stub that only
prints its version. (`README.md` lines 19–24; `gestureos/cli.py`; `pyproject.toml`
`Development Status :: 2 - Pre-Alpha`.)

## 4. Product goals (target features — not yet built)

**FACT** (declared as target, per `README.md` lines 30–37):

| Goal | Description |
| --- | --- |
| Gesture cursor control | Move, click, scroll, drag with hand gestures |
| Media control | Play/pause and similar via gesture |
| Multi-screen spatial mapping | Cursor crosses 1–4 screens with correct geometry |
| Gaze-based screen focus | Look at a screen to direct input there |
| Cross-OS control | Linux (X11/`pynput`-class) and Windows (`pywin32`/`pyautogui`/`pygetwindow`) behind one protocol, plus a no-op backend for headless CI |
| Contextual AI | **FACT** planned as Step 10 of the construction plan (`plans/gestureos-construction.md`) |

## 5. Non-goals / constraints on scope

**INFERENCE** — No special hardware or wearables (webcam only). **FACT** — offline/local-first
posture is implied by the chrysa canon (`standards/rules/ai-orchestration.md`), but no
runtime AI feature exists yet to assess. **UNKNOWN** — pricing, distribution channel, and
telemetry/consent model (packaging is deferred to Step 11b).

## 6. Success metric (product-level)

**FACT** — The product is judged on latency: perception→action **p95 < 50 ms**, measured
per stage. This is treated as a hard product requirement ("latency budget is law").
(`CLAUDE.md` line 34; `AGENTS.md` lines 13–14; `DECISIONS.md` D-0003/D-0005.)

## 7. Related requirements

See [`REQUIREMENTS.md`](REQUIREMENTS.md) for the REQ-PROD / REQ-TECH matrix, and
[`ROADMAP.md`](ROADMAP.md) for the phased delivery plan.
