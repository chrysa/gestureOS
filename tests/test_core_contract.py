"""Contract tests: prove the core path is modality-neutral and the bus behaves.

The two-consumer round-trip (gesture-fake AND voice-fake through the same
event -> context -> resolve -> dispatch path) is the executable form of the extraction
invariant: if core ever grew a modality-specific branch, one of these would need to
diverge. They share identical core code.
"""

from __future__ import annotations

import asyncio

import pytest

from core.bus import Bus, FastPath
from core.events import ContextSnapshot, PerceptionEvent
from core.protocols import (
    ActionResolver,
    CommandRegistry,
    ContextProvider,
    ModalityEngine,
    OSController,
)
from core.types import ActionId, ModalityId, Profile, Trigger, TriggerKind
from tests.fakes import (
    GESTURE,
    VOICE,
    FakeContext,
    FakeGestureEngine,
    FakeRegistry,
    FakeResolver,
    FakeVoiceEngine,
    GestureConfig,
    GesturePayload,
    RecordingOSController,
    VoiceConfig,
    VoicePayload,
)

CTX = ContextSnapshot(
    active_app="editor",
    focused_window="main",
    screen_id=1,
    profile_id="work",
    timestamp_ms=0.0,
)


def _gesture_event() -> PerceptionEvent[GesturePayload]:
    return PerceptionEvent(
        modality_id=GESTURE,
        trigger=Trigger(TriggerKind.GESTURE, GESTURE, "pinch"),
        payload=GesturePayload(),
        timestamp_ms=1.0,
    )


def _voice_event() -> PerceptionEvent[VoicePayload]:
    return PerceptionEvent(
        modality_id=VOICE,
        trigger=Trigger(TriggerKind.VOICE_INTENT, VOICE, "click"),
        payload=VoicePayload(transcript="click"),
        timestamp_ms=1.0,
    )


async def _run_through_core(engine: ModalityEngine, resolver: ActionResolver, os_ctl: RecordingOSController) -> None:
    ctx: ContextProvider = FakeContext(CTX)
    async for event in engine.stream():
        request = resolver.resolve(event, ctx.snapshot())
        if request is not None:
            os_ctl.dispatch(request)


@pytest.mark.asyncio
async def test_two_modalities_share_identical_core_path() -> None:
    registry = FakeRegistry()
    registry.register(Trigger(TriggerKind.GESTURE, GESTURE, "pinch"), ActionId("cursor.click"))
    registry.register(Trigger(TriggerKind.VOICE_INTENT, VOICE, "click"), ActionId("cursor.click"))
    resolver = FakeResolver(registry)

    gesture_os = RecordingOSController()
    voice_os = RecordingOSController()

    # Identical function, two modalities — the modality-neutrality proof.
    await _run_through_core(FakeGestureEngine([_gesture_event()]), resolver, gesture_os)
    await _run_through_core(FakeVoiceEngine([_voice_event()]), resolver, voice_os)

    assert [r.action_id for r in gesture_os.dispatched] == [ActionId("cursor.click")]
    assert [r.action_id for r in voice_os.dispatched] == [ActionId("cursor.click")]


def test_unregistered_trigger_resolves_to_nothing() -> None:
    resolver = FakeResolver(FakeRegistry())
    assert resolver.resolve(_gesture_event(), CTX) is None


def test_profile_holds_configs_opaquely() -> None:
    profile = Profile(
        profile_id="work",
        name="Work",
        modality_configs={GESTURE: GestureConfig(), VOICE: VoiceConfig()},
    )
    # Core only ever sees ModalityConfig; it reads the key, not gesture-specific fields.
    cfg = profile.config_for(GESTURE)
    assert cfg is not None
    assert cfg.modality_id == GESTURE
    assert profile.config_for(ModalityId("eye")) is None


def test_fakes_satisfy_protocols() -> None:
    assert isinstance(FakeGestureEngine([]), ModalityEngine)
    assert isinstance(FakeRegistry(), CommandRegistry)
    assert isinstance(FakeResolver(FakeRegistry()), ActionResolver)
    assert isinstance(RecordingOSController(), OSController)
    assert isinstance(FakeContext(CTX), ContextProvider)


@pytest.mark.asyncio
async def test_bus_fans_out_to_subscribers() -> None:
    bus = Bus(max_queue=8)
    received: list[object] = []

    async def handler(event: object) -> None:
        received.append(event)

    bus.subscribe("context", handler)
    bus.publish("context", CTX)
    await asyncio.sleep(0.01)
    await bus.aclose()
    assert received == [CTX]


@pytest.mark.asyncio
async def test_bus_drops_oldest_on_full_queue() -> None:
    bus = Bus(max_queue=2)
    gate = asyncio.Event()
    seen: list[int] = []

    async def slow(event: object) -> None:
        await gate.wait()
        assert isinstance(event, int)
        seen.append(event)

    sub = bus.subscribe("hot", slow)
    for i in range(10):
        bus.publish("hot", i)
    assert sub.dropped > 0  # newest-wins backpressure kicked in
    gate.set()
    await bus.aclose()


def test_fastpath_is_synchronous_inline() -> None:
    fp: FastPath[int] = FastPath()
    out: list[int] = []
    fp.connect(out.append)
    fp.emit(42)
    assert out == [42]  # no await — inline dispatch on the hot path
