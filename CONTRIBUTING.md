# Contributing to gestureOS

Part of the **chrysa** ecosystem; follows the shared conventions below.

## Prerequisites

```bash
gh auth status      # authenticated as chrysa
pip install pre-commit && pre-commit install
make dev
```

## Branch naming

| Type | Pattern | Example |
|------|---------|---------|
| Feature | `feat/<slug>` | `feat/cursor-move` |
| Bug fix | `fix/<slug>` | `fix/calibration-drift` |
| Chore / CI | `chore/<slug>` | `chore/update-deps` |
| Documentation | `docs/<slug>` | `docs/manual-smoke` |
| Refactoring | `refactor/<slug>` | `refactor/extract-core` |

## Commit format

All commits follow [Conventional Commits](https://www.conventionalcommits.org/):
`<type>(<scope>): <description>`. Enforced by `conventional-pre-commit` (commit-msg).

## Before opening a PR

```bash
make lint          # ruff
make typecheck     # mypy
make docker-test   # tests in Docker (canonical)
make imports       # core/ extraction invariant (once core/ exists)
```

All checks green, CI green. One construction-plan step per PR where practical.
