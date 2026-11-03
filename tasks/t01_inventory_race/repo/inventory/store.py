"""Stock storage.

Production uses a thin client around a remote key-value service. Each call is a
network round trip and is atomic on its own, but there is no compare-and-set and no
multi-key transaction. `InMemoryStockStore` mirrors that contract for local use.
"""

from __future__ import annotations

import threading
from typing import Protocol


class StockStore(Protocol):
    def get(self, sku: str) -> int:
        """Return units currently available for `sku` (0 if unknown)."""
        ...

    def set(self, sku: str, quantity: int) -> None:
        """Overwrite the available units for `sku`."""
        ...


class InMemoryStockStore:
    def __init__(self, initial: dict[str, int] | None = None) -> None:
        self._data = dict(initial or {})
        self._lock = threading.Lock()

    def get(self, sku: str) -> int:
        with self._lock:
            return self._data.get(sku, 0)

    def set(self, sku: str, quantity: int) -> None:
        with self._lock:
            self._data[sku] = quantity
