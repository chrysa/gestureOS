"""Fake modality consumers used to prove the core path is modality-neutral.

Deliberately TWO modalities (gesture + voice) so the contract test shows core routing
both through the identical path with zero modality-specific code inside ``core``. These
live in tests, never in ``core`` — that is the whole point of the extraction invariant.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Sequence
from dataclasses import dataclass, field

from core.events import (
    ActionRequest,
    ActionResult,
    ContextSnapshot,
    PerceptionEvent,
)
from core.types import ActionId, ModalityId, Trigger, TriggerKind

GESTURE = ModalityId("gesture")
VOICE = ModalityId("voice")


# --- modality-owned payloads (would live in gestureos.modalities / voiceos) ----------
@dataclass(frozen=True, slots=True)
class GesturePayload:
    modality_id: ModalityId = GESTURE
    landmark_count: int = 21


@dataclass(frozen=True, slots=True)
class VoicePayload:
    modality_id: ModalityId = VOICE
    transcript: str = ""


# --- modality-owned config (opaque to core) ------------------------------------------
@dataclass(frozen=True, slots=True)
class GestureConfig:
    modality_id: ModalityId = GESTURE
    pinch_threshold: float = 0.05


@dataclass(frozen=True, slots=True)
class VoiceConfig:
    modality_id: ModalityId = VOICE
    wake_word: str = "computer"


# --- fake engines --------------------------------------------------------------------
@dataclass(slots=True)
class FakeGestureEngine:
    events: Sequence[PerceptionEvent[GesturePayload]]

    @property
    def modality_id(self) -> ModalityId:
        return GESTURE

    async def stream(self) -> AsyncIterator[PerceptionEvent[GesturePayload]]:
        for event in self.events:
            yield event


@dataclass(slots=True)
class FakeVoiceEngine:
    events: Sequence[PerceptionEvent[VoicePayload]]

    @property
    def modality_id(self) -> ModalityId:
        return VOICE

    async def stream(self) -> AsyncIterator[PerceptionEvent[VoicePayload]]:
        for event in self.events:
            yield event


# --- fake core-side collaborators ----------------------------------------------------
@dataclass(slots=True)
class FakeContext:
    snap: ContextSnapshot

    def snapshot(self) -> ContextSnapshot:
        return self.snap


@dataclass(slots=True)
class FakeRegistry:
    table: dict[tuple[TriggerKind, ModalityId, str], ActionId] = field(default_factory=dict)

    def register(self, trigger: Trigger, action_id: ActionId) -> None:
        self.table[(trigger.kind, trigger.modality_id, trigger.name)] = action_id

    def action_for(self, trigger: Trigger) -> ActionId | None:
        return self.table.get((trigger.kind, trigger.modality_id, trigger.name))


@dataclass(slots=True)
class FakeResolver:
    registry: FakeRegistry

    def resolve(self, event: PerceptionEvent[object], context: ContextSnapshot) -> ActionRequest | None:
        action_id = self.registry.action_for(event.trigger)
        if action_id is None:
            return None
        return ActionRequest(action_id=action_id, params={"screen": context.screen_id or 0})


@dataclass(slots=True)
class RecordingOSController:
    dispatched: list[ActionRequest] = field(default_factory=list)

    def move_cursor(self, x: int, y: int) -> ActionResult:
        return ActionResult(ActionId("cursor.move"), ok=True)

    def click(self, button: str = "left") -> ActionResult:
        return ActionResult(ActionId("cursor.click"), ok=True)

    def scroll(self, dx: int, dy: int) -> ActionResult:
        return ActionResult(ActionId("cursor.scroll"), ok=True)

    def drag(self, x: int, y: int, button: str = "left") -> ActionResult:
        return ActionResult(ActionId("cursor.drag"), ok=True)

    def focus_window(self, window_id: str) -> ActionResult:
        return ActionResult(ActionId("window.focus"), ok=True)

    def list_windows(self) -> Sequence[str]:
        return ()

    def enumerate_screens(self) -> Sequence[tuple[int, int, int, int]]:
        return ((0, 0, 1920, 1080),)

    def dispatch(self, request: ActionRequest) -> ActionResult:
        self.dispatched.append(request)
        return ActionResult(request.action_id, ok=True, detail="recorded")
