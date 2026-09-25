# SECURITY — gestureOS

> Security posture snapshot from a documentation-only review. This pass does **not** modify
> code. Findings for the owner are flagged by severity. No secrets are reproduced here.

## Secret scan result

**FACT** — No hardcoded secrets, API keys, tokens, passwords, or private keys were found in
tracked source, config, or docs. Matches for "secret"/"token" are limited to:
- Detection tooling and rule text (`scripts/quality_gate.py`, `scripts/gen_context_files.py`,
  `ai-instructions.md` — "never hardcode a secret").
- No `.env` / `.env.example` files exist; the project has no runtime network/API
  integration yet.

**Result: CLEAN (no findings).**

## Attack surface (today)

**FACT** — The shipped code is a CLI version stub plus in-process `core/` primitives
(protocols, dataclass events, an asyncio bus, latency helpers). There is:
- No network listener, no web/API surface, no database, no deserialization of untrusted
  input, no file upload, no auth surface.
- No user-supplied input beyond CLI invocation.

So the current runtime attack surface is effectively nil. **No HIGH/CRITICAL findings.**

## Controls in place

**FACT**
- **Secret scanning gate:** `.github/workflows/secret-scan.yml` (CI) + pre-commit hook.
- **Pre-commit baseline** adopted from chrysa shared-standards (Full baseline; `DECISIONS.md`
  final ADR). Includes conventional-commit lint, ruff, mypy, import-linter, etc.
  (`.pre-commit-config.yaml`.)
- **Branch protection / review:** `main` protected; one approval required; typed PRs.

## Forward-looking risks (INFERENCE — for when the pipeline is built)

These are **not** current defects; they are areas the owner should design for as features
land (per `README.md` target + `plans/gestureos-construction.md`):

1. **Camera/privacy** — the product ingests a live webcam feed. A consent/enablement model,
   local-only processing guarantee, and a visible "camera active" indicator will be needed
   (offline-first is already the chrysa canon posture). Severity when built: **MEDIUM**.
2. **OS control authority** — the `OSController` backends will synthesize mouse/keyboard
   events and manipulate windows. A misfire or hijack of the perception input could drive
   arbitrary input. A kill-switch / pause gesture and rate/scope limits are advisable.
   Severity when built: **MEDIUM**.
3. **Model asset provenance** — MediaPipe `.task` model assets are downloaded (D-0003);
   verify integrity (checksum/pinned source) when that download path is implemented.
   Severity when built: **LOW–MEDIUM**.

## Definition of done (owner)

- No open HIGH/CRITICAL findings today. Nothing to remediate in code from this pass.
- Revisit this file when Steps 3 (OS control) and 6a (vision) introduce real input and
  external assets.
