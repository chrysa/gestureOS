"""Core value types — modality-agnostic identifiers and configuration.

Nothing here may reference a concrete modality (gesture/voice/eye). Modalities define
their own config types that *implement* :class:`ModalityConfig` and register them; core
only ever sees the opaque protocol. This keeps ``Profile`` free of modality fields
(DECISIONS.md D-0002).
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from typing import NewType, Protocol, runtime_checkable

# A stable identifier for an action the system can perform (e.g. "cursor.move").
ActionId = NewType("ActionId", str)

# A stable identifier for an input modality (e.g. "gesture", "voice", "eye").
ModalityId = NewType("ModalityId", str)


class TriggerKind(StrEnum):
    """What kind of perception can fire a command."""

    GESTURE = "gesture"
    VOICE_INTENT = "voice_intent"
    GAZE_TARGET = "gaze_target"
    COMPOSITE = "composite"


@dataclass(frozen=True, slots=True)
class Trigger:
    """A named trigger of a given kind, owned by a modality.

    ``name`` is opaque to core (e.g. a gesture name, an intent id); core only routes it.
    """

    kind: TriggerKind
    modality_id: ModalityId
    name: str


@runtime_checkable
class ModalityConfig(Protocol):
    """Opaque per-modality configuration.

    Core never inspects concrete fields (pinch threshold, wake word, ...). Each modality
    defines a dataclass implementing this protocol and stores it in a :class:`Profile`.
    """

    @property
    def modality_id(self) -> ModalityId: ...


@dataclass(frozen=True, slots=True)
class Profile:
    """A named profile. Modality-agnostic: configs are held opaquely, keyed by modality.

    Core may read ``profile_id`` / ``name`` and pass ``modality_configs[id]`` back to the
    owning modality, but never reaches into a config's modality-specific fields.
    """

    profile_id: str
    name: str
    modality_configs: Mapping[ModalityId, ModalityConfig]

    def config_for(self, modality_id: ModalityId) -> ModalityConfig | None:
        return self.modality_configs.get(modality_id)
