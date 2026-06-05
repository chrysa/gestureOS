"""Asyncio pub/sub bus for fan-out, plus a synchronous fast-path for the hot loop.

Design decision (DECISIONS.md will record under perf): the bus is reserved for
**fan-out** consumers where a few ms of queueing is fine — context updates, the
dashboard, logging. The **perception -> action** chain does NOT go through the bus; it
uses :class:`FastPath`, a direct synchronous call, to protect the < 50 ms p95 budget
(an async queue hop per frame would burn budget and add jitter).

The bus is backpressure-aware: each subscriber has a bounded queue. When full, the
oldest event is dropped (newest-wins) and counted, so a slow consumer can never stall
publishers on the hot path.
"""

from __future__ import annotations

import asyncio
from collections import defaultdict
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field

Subscriber = Callable[[object], Awaitable[None]]


@dataclass(slots=True)
class _Subscription:
    handler: Subscriber
    queue: asyncio.Queue[object]
    dropped: int = 0


@dataclass(slots=True)
class Bus:
    """Topic -> async subscribers, bounded and non-blocking for publishers."""

    max_queue: int = 256
    _subs: dict[str, list[_Subscription]] = field(default_factory=lambda: defaultdict(list))
    _tasks: set[asyncio.Task[None]] = field(default_factory=set)

    def subscribe(self, topic: str, handler: Subscriber) -> _Subscription:
        sub = _Subscription(handler=handler, queue=asyncio.Queue(maxsize=self.max_queue))
        self._subs[topic].append(sub)
        task = asyncio.ensure_future(self._drain(sub))
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)
        return sub

    def publish(self, topic: str, event: object) -> None:
        """Non-blocking publish. Drops oldest on a full subscriber queue (newest-wins)."""
        for sub in self._subs.get(topic, ()):
            if sub.queue.full():
                _discard_oldest(sub)
            sub.queue.put_nowait(event)

    async def _drain(self, sub: _Subscription) -> None:
        while True:
            event = await sub.queue.get()
            try:
                await sub.handler(event)
            finally:
                sub.queue.task_done()

    async def aclose(self) -> None:
        for task in list(self._tasks):
            task.cancel()
        for task in list(self._tasks):
            try:
                await task
            except asyncio.CancelledError:
                pass


def _discard_oldest(sub: _Subscription) -> None:
    try:
        sub.queue.get_nowait()
        sub.queue.task_done()
        sub.dropped += 1
    except asyncio.QueueEmpty:  # pragma: no cover - racy edge, queue drained meanwhile
        pass


@dataclass(slots=True)
class FastPath[T]:
    """Direct synchronous dispatch for the latency-critical perception -> action chain.

    Not a queue: calling :meth:`emit` invokes each handler inline, in order, so the
    per-frame cost is just the handler work (measured by the latency harness).
    """

    _handlers: list[Callable[[T], None]] = field(default_factory=list)

    def connect(self, handler: Callable[[T], None]) -> None:
        self._handlers.append(handler)

    def emit(self, event: T) -> None:
        for handler in self._handlers:
            handler(event)
