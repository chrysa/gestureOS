# TESTING — gestureOS

> Verified against the repo. Commands below are transcribed from `Makefile` and
> `pyproject.toml`; they were **not executed** by this documentation pass (docs-only).

## Test suite (present)

| File | Covers |
| --- | --- |
| `tests/test_smoke.py` | Package import / version stub sanity |
| `tests/test_core_contract.py` | Two-fake-consumer extraction contract (gesture-fake + voice-fake through the identical core path) |
| `tests/test_perf.py` | Latency measurement helpers (`gestureos/perf.py`) |
| `tests/test_benchmark.py` | Latency harness / budget assertions |
| `tests/fakes.py` | Shared fake modality/consumer/backends for the contract test |
| `tests/__init__.py` | Package marker |

## How tests run

**FACT** — Canonical path (mirrors CI deps, includes MediaPipe system libs):

```bash
make docker-test   # docker build --target test -f Dockerfile.test -t gestureos-test . && docker run --rm ...
```

**FACT** — Host targets exist as developer conveniences (but docs say never run the host
toolchain directly — see `TRD.md` §4 contradiction):

```bash
make test          # pytest tests/ -v
make test-cov      # pytest with coverage (term-missing + xml)
make imports       # lint-imports (core/ extraction invariant)
make bench         # python -m benchmarks.latency (glue sub-budget on no-op backend)
make lint          # ruff check
make typecheck     # mypy
make pre-commit    # pre-commit run --all-files
make ci            # lint + typecheck + test
```

## Configuration

**FACT** (`pyproject.toml` `[tool.pytest.ini_options]`):
- `addopts = "--cov=core --cov=gestureos --cov-report=xml --cov-report=term-missing --cov-fail-under=80"`
- `pytest-asyncio` for async tests; `pytest-mock` available.
- `PLR2004` (magic-value) relaxed under `tests/`; mypy decorator rule relaxed for tests.

## Coverage & gates

**FACT** — Coverage gate: **≥ 80%** over `core` + `gestureos`. CI job `test` produces
`reports/coverage.xml`, consumed by the `sonar` job. (`ci.yml`, `sonar.yml`,
`sonar-project.properties`.)

## Latency testing

**FACT** — `make bench` runs the harness on the **no-op backend** and asserts only the
**glue sub-budget (p95 < 5 ms)**. The real end-to-end p95 < 50 ms check is blocked on
committed frame fixtures (`benchmarks/fixtures/`), populated at plan Step 6a. Stages:
`capture | inference | landmark_to_gesture | resolve | dispatch | os_call`.
(`benchmarks/fixtures/README.md`; `gestureos/perf.py`.)

## Manual smoke

**FACT** — A manual smoke procedure is documented in
[`docs/manual-smoke.md`](docs/manual-smoke.md).
