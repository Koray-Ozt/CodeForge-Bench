import pytest
from inventory import InsufficientStock, ReservationNotFound, ReservationService
from support import FakeClock, LatencyStore, Rendezvous, run_concurrently


@pytest.fixture
def store():
    s = LatencyStore()
    s.inner.set("A", 10)
    s.inner.set("B", 4)
    return s


@pytest.fixture
def clock():
    return FakeClock()


@pytest.fixture
def service(store, clock):
    return ReservationService(store, ttl_seconds=60, clock=clock)


def test_reserve_decrements_stock(service):
    reservation = service.reserve("A", 3, "alice")
    assert service.available("A") == 7
    assert reservation.sku == "A" and reservation.quantity == 3
    assert service.active_count() == 1


def test_reserve_more_than_available_raises_and_keeps_stock(service):
    with pytest.raises(InsufficientStock) as info:
        service.reserve("B", 5, "alice")
    assert info.value.available == 4
    assert service.available("B") == 4


@pytest.mark.parametrize("quantity", [0, -1])
def test_non_positive_quantity_rejected(service, quantity):
    with pytest.raises(ValueError):
        service.reserve("A", quantity, "alice")


def test_release_returns_units_once(service):
    reservation = service.reserve("A", 3, "alice")
    assert service.release(reservation.id) is True
    assert service.available("A") == 10
    assert service.release(reservation.id) is False
    assert service.available("A") == 10


def test_confirm_keeps_units_taken(service):
    reservation = service.reserve("A", 3, "alice")
    service.confirm(reservation.id)
    assert service.available("A") == 7
    with pytest.raises(ReservationNotFound):
        service.confirm(reservation.id)
    assert service.release(reservation.id) is False


def test_sweep_releases_only_expired_holds(service, clock):
    old = service.reserve("A", 2, "alice")
    clock.advance(30)
    fresh = service.reserve("A", 1, "bob")
    clock.advance(31)  # old is 61s old, fresh is 31s old
    assert service.sweep_expired() == 1
    assert service.available("A") == 9
    assert service.release(old.id) is False
    assert service.release(fresh.id) is True


def test_reserve_many_rolls_back_on_failure(service):
    with pytest.raises(InsufficientStock):
        service.reserve_many({"A": 2, "B": 9}, "alice")
    assert service.available("A") == 10
    assert service.available("B") == 4
    assert service.active_count() == 0


def test_concurrent_reserves_do_not_oversell(store, service):
    store.inner.set("LAST", 1)
    store.hook = Rendezvous(parties=2)
    results = run_concurrently(
        [lambda: service.reserve("LAST", 1, "alice"), lambda: service.reserve("LAST", 1, "bob")]
    )
    won = [r for r in results if not isinstance(r, BaseException)]
    lost = [r for r in results if isinstance(r, InsufficientStock)]
    assert len(won) == 1 and len(lost) == 1, results
    assert service.available("LAST") == 0
