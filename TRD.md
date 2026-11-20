# TRD — gestureOS

> Technical Requirements Document. Tags: **FACT** / **INFERENCE** / **UNKNOWN**.
> Sources are given inline. See [`REQUIREMENTS.md`](REQUIREMENTS.md) for the requirement matrix.

## 1. Runtime & language

**FACT**
- Python **3.14** runtime (pinned). (`CLAUDE.md` line 31; `DECISIONS.md` D-0003;
  `pyproject.toml` classifier `Programming Language :: Python :: 3.14`.)
- ruff `target-version = "py313"` deliberately (py314 formatter strips multi-except
  parens — D-0004; `pyproject.toml` `[tool.ruff]` comment).
- Object-oriented, one class per file; import the item not the module; named-argument
  call sites (chrysa canon `standards/rules/backend-python.md`).

## 2. Dependencies (declared)

**FACT** (`pyproject.toml`):

| Dependency | Constraint | Purpose |
| --- | --- | --- |
| `mediapipe` | `>=0.10.35` | Vision (Tasks API) |
| `opencv-python-headless` | `>=4.13` | Frame capture / processing (headless) |
| `numpy` | `>=2.0` | Array math |
| `pydantic` | `>=2.7` | Typed models |
| `pydantic-settings` | `>=2.3` | Config |
| `click` | `>=8.1` | CLI |
| `rich` | `>=13.0` | Terminal output |
| `screeninfo` | `>=0.8` | Multi-screen geometry |
| Windows extras | `pyautogui>=0.9.54`, `pywin32>=306`, `pygetwindow>=0.0.9` (`sys_platform=='win32'`) | Windows OS control |
| Dev | `pytest>=8`, `pytest-asyncio`, `pytest-cov>=5`, `pytest-mock`, `ruff>=0.8`, `mypy>=1.10`, `pre-commit>=4`, `import-linter>=2` | Tooling |

**FACT** — Build backend: `hatchling`; packaged modules: `core`, `gestureos`.

## 3. Non-functional requirements

**FACT**
- **Latency:** perception→action **p95 < 50 ms**, measured per stage
  (`capture | inference | landmark_to_gesture | resolve | dispatch | os_call`). Until real
  frame fixtures exist (Step 6a), the harness asserts a **glue sub-budget p95 < 5 ms** on
  the no-op backend. (`benchmarks/fixtures/README.md`; `benchmarks/latency.py`;
  `gestureos/perf.py`.)
- **Test coverage gate:** `--cov-fail-under=80` over `core` + `gestureos`
  (`pyproject.toml` `[tool.pytest.ini_options].addopts`).
- **Extraction invariant:** `core` may not import `gestureos` (import-linter).

## 4. Build / test execution model

**FACT** — Tests and linters run **in Docker** (`Dockerfile.test`, `make docker-test`) or
via pre-commit — never directly on the host, because MediaPipe needs system libs
(`libgl1 libglib2.0-0 libxcb1 libgles2 libegl1`) baked into the image. (`README.md`
lines 46–47, 88–89; `AGENTS.md` lines 11–12; `DECISIONS.md` D-0003.)

**FACT** — Makefile is `makefile-tier: lib`. Targets: `install`, `dev`, `test`, `test-cov`,
`docker-test`, `lint`, `format`, `typecheck`, `imports`, `bench`, `build`, `pre-commit`,
`clean`, `run`, `ci`. (`Makefile`.)

> **CONTRADICTION (documented, not fixed):** `README.md`/`AGENTS.md` say never run
> pytest/ruff/mypy on the host, yet `Makefile` `test`/`lint`/`typecheck`/`bench`/`run`
> targets and `make dev` (`pip install -e`) invoke the host toolchain directly. Only
> `make docker-test` is containerised. The canonical path per docs is `make docker-test`
> or pre-commit; the host targets appear to be developer conveniences. Owner to reconcile.

## 5. CI / release

**FACT** — CI (`.github/workflows/ci.yml`) runs **tests + sonar only**; lint (ruff/mypy/
pre-commit) runs locally via pre-commit and is replayed in CI at release time
(`release.yml` lint gate), to gate PRs without per-push lint billing. Required status
checks: `test`, `sonar`. Coverage travels between jobs as an artifact
(`reports/coverage.xml`). Many process workflows exist (approved-label, auto-assign,
labeler, detect-conflicts, enforce-shortcut-link, pr-dependencies, pull-request-size,
secret-scan, sync-labels, update-pr-body, dependabot-auto-merge).

## 6. Configuration & secrets

**FACT** — No `.env` / `.env.example` present; no runtime secrets in the codebase (no
network/API integrations yet). Secret scanning runs in CI (`secret-scan.yml`) and
pre-commit. **UNKNOWN** — future config surface (settings via `pydantic-settings`) is
declared as a dependency but no settings module exists yet.

## 7. Open technical unknowns

- **UNKNOWN** — Linux OS-control backend library (unspecified in code).
- **UNKNOWN** — Real end-to-end latency on the reference machine (validated at Step 1b/6a
  per D-0003; only headless ~17 ms CPU inference on 256×256 measured so far).
- **UNKNOWN** — Dashboard stack detail beyond "PyQt6 Dashboard" (Step 11 in the plan).
