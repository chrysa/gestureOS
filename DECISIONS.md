# DECISIONS — gestureos

> Repository-local ADRs (Architectural Decision Records). Numbering: D-XXXX.
> Any deviation from `CODE_MANIFEST.md` (chrysa global standards) must be documented here.

---

## D-0001 — Adherence to chrysa global standards

**Date**: 2026-06-04
**Status**: accepted

This project follows all conventions defined in `CODE_MANIFEST.md` (chrysa portfolio
standards). Deviations below.

---

## D-0002 — Option A "extract-after" for the shared core

**Date**: 2026-06-04
**Status**: accepted

gestureOS and voiceOS were re-separated from the frozen ChrysaOS fusion. The ~80 %
shared modules (Context Engine, Action Resolver, Command Registry, OS Control Layer)
are isolated in an internal `core/` package built here first. `core/` is extracted into
a shared library only when voiceOS starts (rule of three — wait for the second real
consumer). No shared lib is built upfront. Multimodal fusion may return later as an
optional third consumer of the core. The extraction invariant (no modality-specific
type leaks into `core/`) is enforced by **import-linter** + a two-fake-consumer test,
from Step 2 onward.

---

## D-0003 — Runtime Python 3.14, MediaPipe Tasks API (not legacy `solutions`)

**Date**: 2026-06-04
**Status**: accepted

Dependency spike (Step 0) result, verified in Docker `python:3.14-slim`:

- `mediapipe==0.10.35`, `opencv-python-headless==4.13.0`, `numpy==2.4.6` all install and
  import on **Python 3.14**. Runtime pinned to 3.14.
- **The legacy `mediapipe.solutions` API is removed** in 0.10.35 (absent on both 3.13 and
  3.14). The vision layer **must use the MediaPipe Tasks API**
  (`mediapipe.tasks.python.vision.HandLandmarker` / `FaceLandmarker`) with a downloaded
  `.task` model asset — not `mp.solutions.hands.Hands`.
- Headless CPU inference on a 256×256 frame measured ~17 ms — leaves headroom under the
  50 ms perception→action budget. Validate on the real reference machine at Step 1b/6a.
- Required system libs (Dockerfile.test / CI): `libgl1 libglib2.0-0 libxcb1 libgles2
  libegl1`.
- `opencv-python-headless` is used (not `opencv-python`) so CI and `Dockerfile.test`
  import cleanly without an X server; `cv2.VideoCapture` still works on desktop.

---

## D-0004 — ruff `target-version = py313` despite 3.14 runtime

**Date**: 2026-06-04
**Status**: accepted

`ruff format` (<= 0.15.15) strips multi-`except` parentheses under `target-version = py314`,
producing invalid Python (org-wide chrysa bug, ~20 repos). Pin `target-version = "py313"`
in `pyproject.toml`. Revert once the upstream ruff fix ships.

---

## D-0005 — Bus for fan-out, synchronous FastPath for perception→action

**Date**: 2026-06-04
**Status**: accepted

`core.bus.Bus` (asyncio pub/sub, bounded, newest-wins backpressure) is used only for
**fan-out** consumers (context, dashboard, logging) where a few ms of queueing is
acceptable. The **perception→action** hot chain uses `core.bus.FastPath` — direct
synchronous inline dispatch, no queue hop — to protect the < 50 ms p95 latency budget
(D-0003 / Step 1b). An async queue per frame would add latency and jitter on the path
that the product is judged on.
