# REVIEW — gestureOS documentation pass

> Documentation-only review (no source/test/config changed). Records what was generated,
> contradictions found, key unknowns, and documentation debt. Date: 2026-09-25.

## Scope

Root-level Markdown documentation generated from repository evidence. No code, tests,
dependencies, CI, or config were modified. Existing docs were preserved.

## Documents generated (root)

`PRD.md`, `TRD.md`, `ARCHITECTURE.md`, `REQUIREMENTS.md`, `CONSTRAINTS.md`, `TESTING.md`,
`SECURITY.md`, `OBSERVABILITY.md`, `ROADMAP.md`, `GLOSSARY.md`, `REVIEW.md`.

## Documents NOT generated (and why)

- **DECISIONS.md** — already exists and is authoritative (ADRs D-0001…D-0005 + CI/pre-commit
  ADR). Preserved untouched; the new docs reference it.

## Existing docs preserved

`README.md`, `CLAUDE.md`, `AGENTS.md`, `CONTRIBUTING.md`, `CHANGELOG.md`, `DECISIONS.md`,
`docs/architecture.md`, `docs/manual-smoke.md`, `docs/reference/github-inspiration.md`,
`plans/gestureos-construction.md`, `benchmarks/fixtures/README.md`, generated context files
(`handover.md`, `ai-instructions.md`, `context-map.json`, `llms-full.txt`). None were edited.

## Contradictions found

1. **Host vs Docker test execution.** `README.md`/`AGENTS.md`/`CONTRIBUTING.md` state
   pytest/ruff/mypy must never run on the host (Docker or pre-commit only), yet the
   `Makefile` `test`/`lint`/`typecheck`/`bench`/`run` targets and `make dev` invoke the host
   toolchain directly; only `make docker-test` is containerised. Documented in `TRD.md` §4
   and `TESTING.md`. Owner to reconcile (likely: host targets are conveniences).
2. **Branch model wording.** `CONTRIBUTING.md` branches from `main`; the chrysa canon block
   describes a `main`(prod)/`develop`(workspace) model. Current working branch is
   `chore/claude-config-drift-hook`. Minor; noted in `CONSTRAINTS.md`.

## Key UNKNOWNs

- Concrete Linux OS-control backend library (not fixed in code).
- Real end-to-end latency on the reference machine (only headless ~17 ms inference measured).
- Runtime config/settings surface, logging/error-tracking backend, and metrics export.
- Pricing, distribution channel, telemetry/consent model (packaging = Step 11b).
- Exact per-step completion status (Steps 1/1b/2 inferred DONE from artefacts; only Step 0
  is explicitly ✅ in the plan).

## Documentation debt

- No production `Dockerfile` / `docker-compose` yet (only `Dockerfile.test`) — expected at
  packaging (Step 11b).
- No per-folder `README.md` in `core/`, `gestureos/`, `tests/`, `scripts/` despite the
  repo's own `.claude/rules/folder-readme.md` rule (that rule says add on substantial work,
  not a mass PR — left as-is per docs-only scope).
- Camera privacy / consent and OS-control kill-switch design not yet documented — flagged in
  `SECURITY.md` as forward-looking (MEDIUM) for when the pipeline lands.

## Security summary

Secret scan: **CLEAN** (no hardcoded secrets; no `.env`). Current runtime attack surface is
effectively nil (CLI stub + in-process primitives). No HIGH/CRITICAL findings. See
`SECURITY.md`.

## Overall assessment

Unusually well-governed pre-alpha bootstrap: the architecture, decisions, and multi-PR plan
are already documented and internally consistent. The generated docs formalise the
product/technical requirement matrix, constraints, testing, security, observability, and
roadmap views that were implicit across README/CLAUDE/DECISIONS/plan.
