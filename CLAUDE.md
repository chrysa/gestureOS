# gestureOS — Claude context

## What this project does

Hands-free computer control from a webcam: hand-gesture cursor (move / click / scroll /
drag), multi-screen spatial mapping (1–4 screens), gaze-based screen focus, media control.
Leader project of the re-separated gestureOS / voiceOS pair.

## Architecture (Option A — extract-after)

The ~80 % shared logic lives in an internal **`core/`** package: Context Engine, Action
Resolver, Command Registry, OS Control Layer, plus typed `Protocol`s and an asyncio
pub/sub bus. `core/` is **modality-agnostic** and is the extraction target for a shared
lib once voiceOS starts (D-0002). Modalities (gesture, eye, later voice) implement the
`ModalityEngine` protocol and emit `PerceptionEvent`s; **no modality-specific type may
leak into `core/`** — enforced by **import-linter** + a two-fake-consumer test.

```
core/            protocols, events, bus, types  (no modality, no real OS calls)
gestureos/
  modalities/    gesture, eye  (implement ModalityEngine)
  oscontrol/     per-OS backends behind OSController protocol (+ no-op)
  context/       Context Engine
  resolve/       Command Registry + Action Resolver + Profiles
  app/           composition root + CLI
benchmarks/      latency harness (p50/p95/p99, per-stage)
```

## Key conventions

- **Runtime Python 3.14**; **MediaPipe Tasks API** only (legacy `solutions` removed — D-0003).
- ruff `target-version = "py313"` (py314 formatter bug — D-0004).
- Tests / lint run in **Docker** (`Dockerfile.test`) or pre-commit — never on host.
- Latency budget is law: perception→action **p95 < 50 ms**, measured per stage.
- English for all code, docs, commits, PRs.
- Conventional Commits; branches `feat/` `fix/` `chore/` `docs/` `refactor/`.

## Plan

Full multi-PR construction blueprint: [`plans/gestureos-construction.md`](plans/gestureos-construction.md).
Serial spine: Step 0 (dep spike ✅) → 1 (bootstrap) → 1b (latency harness) → 2 (core/) →
5b (app) → 6a/6b/6c (gesture MVP) → 7/7b (multiscreen) → 8 (eye) → 9 (media) → 10
(contextual AI) → 11b (packaging) → 12 (core/ extraction audit → unblocks voiceOS).

<!-- chrysa:standards-import:start -->
@.chrysa/STANDARDS.md
<!-- chrysa:standards-import:end -->

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
