# AGENTS — gestureOS

Guidance for AI agents working in this repository.

## Golden rules

- **Read `CLAUDE.md` and `DECISIONS.md` first.** They hold the binding architecture and
  runtime decisions (Option A extract-after, Python 3.14, MediaPipe Tasks API, ruff py313).
- **Never let modality-specific types leak into `core/`.** The extraction invariant is the
  whole point of the architecture; import-linter will fail the build if you break it.
- **Run tests and linters in Docker** (`make docker-test`) or via pre-commit — never on the
  host. MediaPipe needs system libs only present in `Dockerfile.test`.
- **Respect the latency budget** (perception→action p95 < 50 ms). Any change on the
  perception→action path must keep `make bench` within budget.
- **Follow the plan.** Work proceeds step by step per `plans/gestureos-construction.md`.
  One step ≈ one PR. Do not start a step whose dependencies are not merged.

## Workflow

1. Branch `feat/<slug>` (or `fix/` / `chore/` / `docs/` / `refactor/`).
2. Implement the smallest slice that satisfies one plan step's exit criteria.
3. `make lint && make typecheck && make docker-test` green.
4. Conventional-commit; open a PR; keep CI green.
