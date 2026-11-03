import sys
import threading

import pytest
from inventory import InsufficientStock, ReservationNotFound, ReservationService
from support import FakeClock, LatencyStore, Rendezvous, run_concurrently


@pytest.fixture
def store():
    s = LatencyStore()
    s.inner.set("A", 10)
    s.inner.set("B", 10)
    return s


@pytest.fixture
def clock():
    return FakeClock()


@pytest.fixture
def service(store, clock):
    return ReservationService(store, ttl_seconds=60, clock=clock)


def test_double_release_credits_units_once(store, service):
    reservation = service.reserve("A", 5, "alice")
    store.hook = Rendezvous(parties=2)
    results = run_concurrently([lambda: service.release(reservation.id)] * 2)
    assert not any(isinstance(r, BaseException) for r in results), results
    assert sorted(results) == [False, True]
    assert store.inner.get("A") == 10


def test_release_and_reserve_do_not_lose_updates(store, service):
    held = service.reserve("A", 5, "alice")  # A: 10 -> 5
    store.hook = Rendezvous(parties=2)
    results = run_concurrently(
        [lambda: service.release(held.id), lambda: service.reserve("A", 2, "bob")]
    )
    assert not any(isinstance(r, BaseException) for r in results), results
    assert store.inner.get("A") == 8  # 5 + 5 returned - 2 taken


def test_different_skus_are_not_serialized(store, service):
    """Store calls are network round trips; a global lock would cap throughput."""
    gate = Rendezvous(parties=2, timeout=2.0)
    store.hook = gate
    results = run_concurrently(
        [lambda: service.reserve("A", 1, "alice"), lambda: service.reserve("B", 1, "bob")]
    )
    assert not any(isinstance(r, BaseException) for r in results), results
    assert gate.met, "reservations for different SKUs never overlapped in the store"


@pytest.mark.parametrize("action", ["release", "sweep"])
def test_confirm_racing_with_release_or_sweep_is_exclusive(store, service, clock, action):
    reservation = service.reserve("A", 4, "alice")  # A: 10 -> 6
    clock.advance(61)
    confirmed: list[bool] = []

    def confirm_from_other_thread() -> None:
        try:
            service.confirm(reservation.id)
            confirmed.append(True)
        except ReservationNotFound:
            confirmed.append(False)

    fired = threading.Event()

    def hook(op: str, sku: str) -> None:
        if op == "get" and not fired.is_set():
            fired.set()
            helper = threading.Thread(target=confirm_from_other_thread, daemon=True)
            helper.start()
            helper.join(0.3)  # a correct fix may make the helper wait; that is fine

    store.hook = hook
    released = service.release(reservation.id) if action == "release" else service.sweep_expired()
    store.hook = None
    for t in threading.enumerate():
        if t is not threading.current_thread() and t.daemon:
            t.join(2)

    units_returned = bool(released)
    assert len(confirmed) == 1
    # Exactly one outcome may win, and stock must agree with it.
    assert confirmed[0] != units_returned, (confirmed, released)
    assert store.inner.get("A") == (10 if units_returned else 6)


def test_lock_not_leaked_after_failed_reserve(store, service):
    with pytest.raises(InsufficientStock):
        service.reserve("A", 99, "alice")
    results = run_concurrently([lambda: service.reserve("A", 1, "bob")], timeout=2.0)
    assert not isinstance(results[0], BaseException), results


def test_lock_not_leaked_after_store_error(store, service):
    calls = {"n": 0}

    def flaky(op: str, sku: str) -> None:
        calls["n"] += 1
        if calls["n"] == 1:
            raise ConnectionError("store unavailable")

    store.hook = flaky
    with pytest.raises(ConnectionError):
        service.reserve("A", 1, "alice")
    store.hook = None
    results = run_concurrently([lambda: service.reserve("A", 1, "bob")], timeout=2.0)
    assert not isinstance(results[0], BaseException), results
    assert store.inner.get("A") == 9


def test_stress_invariants_hold(store, service):
    """Many threads mix reserve/release/confirm; units must be conserved exactly."""
    skus = ["A", "B"]
    store.inner.set("A", 50)
    store.inner.set("B", 50)
    confirmed = {"A": 0, "B": 0}
    confirmed_lock = threading.Lock()

    def worker(seed: int):
        def job():
            for i in range(150):
                sku = skus[(seed + i) % 2]
                try:
                    reservation = service.reserve(sku, 1 + (i % 3), f"w{seed}")
                except InsufficientStock:
                    continue
                if i % 5 == 0:
                    service.confirm(reservation.id)
                    with confirmed_lock:
                        confirmed[sku] += reservation.quantity
                else:
                    assert service.release(reservation.id) is True

        return job

    previous = sys.getswitchinterval()
    sys.setswitchinterval(1e-6)
    try:
        results = run_concurrently([worker(s) for s in range(8)], timeout=60)
    finally:
        sys.setswitchinterval(previous)
    assert not any(isinstance(r, BaseException) for r in results), results
    for sku in skus:
        assert store.inner.get(sku) == 50 - confirmed[sku], sku
    assert service.active_count() == 0
