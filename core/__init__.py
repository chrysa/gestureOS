"""core — modality-agnostic foundation shared by every input modality.

This package is the **extraction target**: it must contain no modality-specific
(gesture / voice / eye) or OS-specific code, so it can later be lifted into a shared
library consumed by both gestureOS and voiceOS (DECISIONS.md D-0002). The invariant
``core`` must not import from ``gestureos`` is enforced by import-linter.
"""

__all__ = ["__version__"]

__version__ = "0.1.0"
