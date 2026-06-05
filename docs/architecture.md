# Architecture

> Binding rules in `DECISIONS.md` (D-0002 extraction, D-0003 vision, D-0005 bus).

## Layers

```
core/                      modality- and OS-agnostic foundation (EXTRACTION TARGET)
  types.py                 ActionId, ModalityId, Trigger, Profile (opaque modality config)
  events.py                PerceptionEvent[P], ContextSnapshot, ActionRequest, ActionResult
  protocols.py             ModalityEngine, ContextProvider, CommandRegistry, ActionResolver,
                           OSController, ProfileStore, CalibrationStore
  bus.py                   asyncio pub/sub (fan-out) + FastPath (perception->action hot loop)

gestureos/                 the application + its modalities (may import core; never the reverse)
  modalities/              gesture, eye  -> implement ModalityEngine, own their payload/config types
  oscontrol/               per-OS OSController backends + no-op/recording backend
  context/ resolve/ app/   Context Engine, Command Registry + Resolver + Profiles, composition root
```

## The extraction invariant

`core` is the ~80 % shared logic that voiceOS will reuse. It must stay free of any
gesture/voice/eye or OS specifics so it can be lifted into a shared library when voiceOS
starts (D-0002). Enforced two ways:

1. **import-linter** forbidden contract: `core` may not import `gestureos`
   (`make imports` / CI).
2. **Two-fake-consumer contract test** (`tests/test_core_contract.py`): a gesture-fake
   AND a voice-fake run through the *identical* `event -> context -> resolve -> dispatch`
   core path. A modality-specific branch in core would force one to diverge.

Modalities never put their fields in core: `PerceptionEvent` is generic over a
modality-owned `payload: P` (bounded by `ModalityPayload`), and `Profile` holds
`Mapping[ModalityId, ModalityConfig]` opaquely.

## Latency: bus vs fast-path (D-0005)

The asyncio `Bus` is for **fan-out** (context, dashboard, logging) where small queueing
latency is fine; it is bounded and newest-wins so a slow consumer never stalls
publishers. The **perception -> action** chain bypasses the bus and uses `FastPath`
(direct synchronous inline dispatch) to protect the < 50 ms p95 budget — an async queue
hop per frame would add latency and jitter.
