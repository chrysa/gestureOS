# gestureOS

> Multi-screen eye & gesture computer control — drive the cursor, click, scroll, drag and
> control media with your hands and gaze, using a plain webcam.

[![CI](https://github.com/chrysa/gestureOS/actions/workflows/ci.yml/badge.svg)](https://github.com/chrysa/gestureOS/actions/workflows/ci.yml)

gestureOS turns a webcam into a hands-free input device: hand-gesture cursor control
(move / click / scroll / drag), multi-screen spatial mapping (1–4 screens), gaze-based
screen focus, and media control. It is the **leader** of a re-separated pair —
[voiceOS](https://github.com/chrysa/voiceOS) is its voice-driven twin; both are built on
the same internal `core/` (see [DECISIONS.md](DECISIONS.md), D-0002).

## Status

**Pre-alpha — bootstrap.** Repository scaffolding only; no working pipeline yet.
The full multi-PR construction plan lives in [`plans/gestureos-construction.md`](plans/gestureos-construction.md).

## Stack

- **Python 3.14** (runtime confirmed by the Step 0 dependency spike — D-0003)
- **MediaPipe Tasks API** (`HandLandmarker` / `FaceLandmarker`) + **OpenCV** for perception
- **OS Control Layer** behind a protocol — Linux (`ydotool` / `wmctrl` / `xdotool`),
  Windows (`pywin32` / `pyautogui` / `pygetwindow`), plus a no-op backend for headless CI
- **asyncio** pub/sub bus for fan-out; a synchronous fast-path for the perception→action chain
- **PyQt6** dashboard (later phase)

## Hard requirement

Perception→action latency **< 50 ms** (p95, real pipeline). Measured per stage
(`capture | inference | landmark→gesture | resolve | dispatch | OS-call`) by `make bench`.

## Development

```bash
make dev          # install deps + pre-commit
make docker-test  # run the test suite in Docker (canonical — mirrors CI deps)
make lint         # ruff check
make typecheck    # mypy
make bench        # latency harness (p50/p95/p99)
```

> Tests and linters run in Docker (`Dockerfile.test`) or via pre-commit — never directly
> on the host. MediaPipe needs system libs (`libgl1 libglib2.0-0 libxcb1 libgles2 libegl1`)
> baked into the test image.

## License

MIT © chrysa
