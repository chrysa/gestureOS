"""Typed structural interfaces every concrete implementation must satisfy.

These ``Protocol``s are the contract VoiceOS will reuse verbatim once ``core`` is
extracted (DECISIONS.md D-0002). No concrete class lives here. Steps 3/4/5 implement
them; Step 5 codes only against :class:`OSController` (fake backend) until Step 3 lands.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Sequence
from typing import Protocol, runtime_checkable

from core.events import ActionRequest, ActionResult, ContextSnapshot, ModalityPayload, PerceptionEvent
from core.types import ActionId, ModalityId, Profile, Trigger


@runtime_checkable
class ModalityEngine(Protocol):
    """Produces a stream of perception events. Gesture/voice/eye implement this identically."""

    @property
    def modality_id(self) -> ModalityId: ...

    def stream(self) -> AsyncIterator[PerceptionEvent[ModalityPayload]]:
        """Yield perception events until cancelled."""
        ...


@runtime_checkable
class ContextProvider(Protocol):
    """Supplies the current desktop context snapshot."""

    def snapshot(self) -> ContextSnapshot: ...


@runtime_checkable
class CommandRegistry(Protocol):
    """Maps triggers to action ids within an allowed context / profile scope."""

    def register(self, trigger: Trigger, action_id: ActionId) -> None: ...

    def action_for(self, trigger: Trigger) -> ActionId | None: ...


@runtime_checkable
class ActionResolver(Protocol):
    """Turns a perception event + context into a concrete action request (or nothing)."""

    def resolve(self, event: PerceptionEvent[ModalityPayload], context: ContextSnapshot) -> ActionRequest | None: ...


@runtime_checkable
class OSController(Protocol):
    """Performs OS-level effects. Backends: Linux, Windows, and a no-op/recording one."""

    def move_cursor(self, x: int, y: int) -> ActionResult: ...

    def click(self, button: str = "left") -> ActionResult: ...

    def scroll(self, dx: int, dy: int) -> ActionResult: ...

    def drag(self, x: int, y: int, button: str = "left") -> ActionResult: ...

    def focus_window(self, window_id: str) -> ActionResult: ...

    def list_windows(self) -> Sequence[str]: ...

    def enumerate_screens(self) -> Sequence[tuple[int, int, int, int]]: ...

    def dispatch(self, request: ActionRequest) -> ActionResult: ...


@runtime_checkable
class ProfileStore(Protocol):
    """Loads named profiles (modality configs held opaquely)."""

    def load(self, profile_id: str) -> Profile: ...

    def list_profiles(self) -> Sequence[str]: ...


@runtime_checkable
class CalibrationStore(Protocol):
    """Persists per-setup calibration (e.g. screen mapping), invalidated on topology change."""

    def save(self, key: str, data: bytes) -> None: ...

    def load(self, key: str) -> bytes | None: ...

    def invalidate(self, key: str) -> None: ...
