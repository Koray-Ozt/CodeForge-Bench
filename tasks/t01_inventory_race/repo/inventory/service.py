"""Stock reservation for the checkout flow.

A reservation holds units of a SKU for a limited time while the customer pays.
`confirm` makes the hold permanent, `release` (or expiry) returns the units.
The service is shared by all request-handling threads in the process.
"""

from __future__ import annotations

import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass

from .store import StockStore


class InsufficientStock(Exception):
    def __init__(self, sku: str, requested: int, available: int) -> None:
        super().__init__(f"{sku}: requested {requested}, available {available}")
        self.sku = sku
        self.requested = requested
        self.available = available


class ReservationNotFound(Exception):
    pass


@dataclass(frozen=True)
class Reservation:
    id: str
    sku: str
    quantity: int
    holder: str
    expires_at: float


class ReservationService:
    def __init__(
        self,
        store: StockStore,
        ttl_seconds: float = 300.0,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self._store = store
        self._ttl = ttl_seconds
        self._clock = clock
        self._reservations: dict[str, Reservation] = {}

    def available(self, sku: str) -> int:
        return self._store.get(sku)

    def reserve(self, sku: str, quantity: int, holder: str) -> Reservation:
        if quantity <= 0:
            raise ValueError("quantity must be positive")
        available = self._store.get(sku)
        if available < quantity:
            raise InsufficientStock(sku, quantity, available)
        self._store.set(sku, available - quantity)
        reservation = Reservation(
            id=uuid.uuid4().hex,
            sku=sku,
            quantity=quantity,
            holder=holder,
            expires_at=self._clock() + self._ttl,
        )
        self._reservations[reservation.id] = reservation
        return reservation

    def reserve_many(self, items: dict[str, int], holder: str) -> list[Reservation]:
        """Reserve every item or none: roll back earlier holds if a later one fails."""
        done: list[Reservation] = []
        try:
            for sku, quantity in items.items():
                done.append(self.reserve(sku, quantity, holder))
        except Exception:
            for reservation in done:
                self.release(reservation.id)
            raise
        return done

    def confirm(self, reservation_id: str) -> Reservation:
        """Make a hold permanent. Units are not returned to stock."""
        reservation = self._reservations.get(reservation_id)
        if reservation is None:
            raise ReservationNotFound(reservation_id)
        del self._reservations[reservation_id]
        return reservation

    def release(self, reservation_id: str) -> bool:
        """Return held units to stock. Returns False if the hold is already gone."""
        reservation = self._reservations.get(reservation_id)
        if reservation is None:
            return False
        self._store.set(
            reservation.sku, self._store.get(reservation.sku) + reservation.quantity
        )
        del self._reservations[reservation_id]
        return True

    def sweep_expired(self) -> int:
        """Release every hold past its expiry. Returns how many were released."""
        now = self._clock()
        released = 0
        for reservation_id, reservation in list(self._reservations.items()):
            if reservation.expires_at <= now and self.release(reservation_id):
                released += 1
        return released

    def active_count(self) -> int:
        return len(self._reservations)
