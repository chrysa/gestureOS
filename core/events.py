"""Core event schemas flowing perception -> context -> resolution -> action.

``PerceptionEvent`` is **generic over a modality-owned payload** (bounded by
:class:`ModalityPayload`) rather than carrying ``payload: Any``. This lets a gesture
module attach a typed ``GesturePayload`` and a voice module a typed ``VoicePayload``
while core stays modality-agnostic and type-safe (DECISIONS.md D-0002).
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

from core.types import ActionId, ModalityId, Trigger


@runtime_checkable
class ModalityPayload(Protocol):
    """Marker for a modality's typed perception payload. Core never reads its fields."""

    @property
    def modality_id(self) -> ModalityId: ...


# Scalar parameter values an action may carry. Deliberately closed (no Any).
ParamValue = str | int | float | bool


@dataclass(frozen=True, slots=True)
class PerceptionEvent[P: ModalityPayload]:
    """A single perception emitted by a :class:`~core.protocols.ModalityEngine`."""

    modality_id: ModalityId
    trigger: Trigger
    payload: P
    timestamp_ms: float


@dataclass(frozen=True, slots=True)
class ContextSnapshot:
    """Modality-agnostic view of the desktop at a point in time."""

    active_app: str | None
    focused_window: str | None
    screen_id: int | None
    profile_id: str | None
    timestamp_ms: float


@dataclass(frozen=True, slots=True)
class ActionRequest:
    """A resolved request to perform an action, ready for the OS control layer."""

    action_id: ActionId
    params: Mapping[str, ParamValue] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ActionResult:
    """Outcome of dispatching an :class:`ActionRequest`."""

    action_id: ActionId
    ok: bool
    detail: str = ""
