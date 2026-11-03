"""Shared helpers for deterministic concurrency tests (no sleeps used for ordering)."""

from __future__ import annotations

import threading
from collections.abc import Callable

from inventory import InMemoryStockStore


class Rendezvous:
    """One-shot barrier on the first `parties` store reads.

    If every party reaches `get` at the same time the barrier opens, which is exactly the
    interleaving that exposes a check-then-act race. A correct implementation serializes the
    parties, so the barrier times out instead and `met` stays False. Both outcomes are
    valid for the code under test; only the final state is asserted.
    """

    def __init__(self, parties: int, timeout: float = 0.3) -> None:
        self._barrier = threading.Barrier(parties)
        self._timeout = timeout
        self._lock = threading.Lock()
        self._entered = 0
        self._parties = parties
        self.met = False

    def __call__(self, op: str, sku: str) -> None:
        if op != "get":
            return
        with self._lock:
            self._entered += 1
            participates = self._entered <= self._parties
        if not participates:
            return
        try:
            self._barrier.wait(self._timeout)
            self.met = True
        except threading.BrokenBarrierError:
            pass


class LatencyStore:
    """Store wrapper that calls `hook(op, sku)` while a call is in flight, like a network hop.

    For `get` the hook runs after the value was read, so a caller holding that value can be
    overtaken by another thread, which is what makes read-modify-write races reproducible.
    """

    def __init__(self, inner: InMemoryStockStore | None = None) -> None:
        self.inner = inner or InMemoryStockStore()
        self.hook: Callable[[str, str], None] | None = None

    def get(self, sku: str) -> int:
        value = self.inner.get(sku)  # the value is read, then the reply is "in flight"
        if self.hook:
            self.hook("get", sku)
        return value

    def set(self, sku: str, quantity: int) -> None:
        if self.hook:
            self.hook("set", sku)
        self.inner.set(sku, quantity)


class FakeClock:
    def __init__(self, now: float = 1000.0) -> None:
        self.now = now

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


def run_concurrently(
    jobs: list[Callable[[], object]], timeout: float = 10.0
) -> list[object | BaseException]:
    """Run each job in its own thread; return results or the exception each raised."""
    results: list[object | BaseException] = [None] * len(jobs)

    def wrap(index: int, job: Callable[[], object]) -> None:
        try:
            results[index] = job()
        except BaseException as exc:  # noqa: BLE001 - we report it to the test
            results[index] = exc

    threads = [threading.Thread(target=wrap, args=(i, j), daemon=True) for i, j in enumerate(jobs)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout)
    assert not any(t.is_alive() for t in threads), "deadlock: worker threads did not finish"
    return results
