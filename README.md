# gestureOS

> Control your computer hands-free with a plain webcam — move the cursor, click, scroll,
> drag and control media using hand gestures and gaze, across up to four screens.

[![CI](https://github.com/chrysa/gestureOS/actions/workflows/ci.yml/badge.svg)](https://github.com/chrysa/gestureOS/actions/workflows/ci.yml)

gestureOS turns any webcam into a hands-free input device. No special hardware, no
wearables — just the camera you already have.

## Who it's for

People who want or need to drive a desktop without a mouse: accessibility users,
hands-busy workflows, multi-screen setups, and anyone building on top of a low-latency
perception→action pipeline.

## Status

**Pre-alpha — bootstrap.** This repository currently ships the `core/` foundation
(typed protocols, event types, the pub/sub bus + latency fast-path) and the latency
harness. The webcam perception and OS-control pipeline is **not implemented yet**, so
the features below describe the target, not what runs today. The CLI is a stub that only
prints its version.

The full multi-PR construction plan lives in
[`plans/gestureos-construction.md`](plans/gestureos-construction.md).

## Planned features

- **Gesture cursor control** — move, click, scroll and drag with hand gestures
  (e.g. pinch → click, two-finger → scroll)
- **Multi-screen spatial mapping** — the cursor crosses 1–4 screens with correct geometry
- **Gaze-based screen focus** — look at a screen to direct input there
- **Media control** — play/pause and friends, hands-free
- **Cross-platform OS layer** — Linux (`ydotool` / `wmctrl` / `xdotool`) and
  Windows (`pywin32` / `pyautogui` / `pygetwindow`) behind one protocol, plus a no-op
  backend for headless CI

gestureOS is the **leader** of a re-separated pair —
[voiceOS](https://github.com/chrysa/voiceOS) is its voice-driven twin; both build on the
same internal `core/` (see [DECISIONS.md](DECISIONS.md), D-0002).

## Requirements

- **Python 3.14**
- A webcam (for the pipeline, once implemented)
- Linux system libs for MediaPipe: `libgl1 libglib2.0-0 libxcb1 libgles2 libegl1`

## Install

```bash
make install      # pip install -e .  (runtime deps)
# or, for development:
make dev          # editable install with [dev] extras + pre-commit hooks
```

## Usage

Today the only working command is the version stub:

```bash
gestureos              # prints version + hint, or:
python -m gestureos
gestureos --help       # list commands
```

The real composition root (camera capture → gesture → OS control) lands in a later step
of the construction plan; this section will grow as the pipeline comes online.

## Performance requirement

Perception→action latency must stay **under 50 ms** (p95, real pipeline), measured
per stage (`capture | inference | landmark→gesture | resolve | dispatch | os_call`):

```bash
make bench        # latency harness — p50/p95/p99 + per-stage budget check
```

## Development

```bash
make docker-test  # run the test suite in Docker (canonical — mirrors CI deps)
make lint         # ruff check
make typecheck    # mypy (strict)
make imports      # verify the core/ extraction invariant (import-linter)
```

> Tests and linters run in Docker (`Dockerfile.test`) or via pre-commit — never directly
> on the host. MediaPipe needs the system libs above baked into the test image.

See [`docs/architecture.md`](docs/architecture.md) for the layer design and the
`core/` extraction invariant, and [`docs/manual-smoke.md`](docs/manual-smoke.md) for the
human-run verification checklist.

## License

MIT © chrysa
