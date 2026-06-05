.DEFAULT_GOAL := help

PYTHON := python3
PKG    := gestureos

.PHONY: help install dev test test-cov docker-test lint format typecheck imports bench clean run

help:  ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install runtime dependencies
	pip install -e .

dev:  ## Install all dev dependencies + pre-commit
	pip install -e ".[dev]"
	pre-commit install

test:  ## Run tests
	pytest tests/ -v

test-cov:  ## Run tests with coverage report
	pytest tests/ -v --cov --cov-report=term-missing --cov-report=xml

docker-test:  ## Run tests inside Docker (canonical, mirrors CI deps)
	docker build --target test -f Dockerfile.test -t gestureos-test .
	docker run --rm gestureos-test

lint:  ## Run linter (ruff check)
	ruff check core $(PKG) benchmarks tests

format:  ## Format code (ruff format)
	ruff format core $(PKG) benchmarks tests

typecheck:  ## Run mypy type checking
	mypy core $(PKG)

imports:  ## Verify core/ extraction invariant (import-linter)
	lint-imports

bench:  ## Run latency harness (p50/p95/p99, per-stage budget)
	$(PYTHON) -m benchmarks.latency

clean:  ## Remove build artefacts
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .coverage coverage.xml .pytest_cache dist build

run:  ## Start gestureOS
	$(PYTHON) -m gestureos
