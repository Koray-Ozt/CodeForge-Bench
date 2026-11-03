"""A tiny in-process WSGI client plus helpers shared by visible and hidden tests."""

from __future__ import annotations

import io
import json
import threading
from dataclasses import dataclass
from typing import Any
from wsgiref.util import setup_testing_defaults

import pytest


@dataclass
class Resp:
    status: int
    headers: dict[str, str]
    body: Any

    @property
    def etag(self) -> str | None:
        return self.headers.get("etag")


class Client:
    def __init__(self, app, customer: str = "c1") -> None:
        self.app = app
        self.customer = customer

    def request(
        self,
        method: str,
        path: str,
        body: Any = None,
        headers: dict[str, str] | None = None,
        raw: bytes | None = None,
        customer: str | None = "default",
    ) -> Resp:
        payload = (
            raw if raw is not None else (json.dumps(body).encode() if body is not None else b"")
        )
        path, _, query = path.partition("?")
        environ: dict[str, Any] = {}
        setup_testing_defaults(environ)
        environ.update(
            REQUEST_METHOD=method,
            PATH_INFO=path,
            QUERY_STRING=query,
            CONTENT_LENGTH=str(len(payload)),
            CONTENT_TYPE="application/json",
        )
        environ["wsgi.input"] = io.BytesIO(payload)
        who = self.customer if customer == "default" else customer
        if who:
            environ["HTTP_X_CUSTOMER_ID"] = who
        for name, value in (headers or {}).items():
            environ["HTTP_" + name.upper().replace("-", "_")] = value

        captured: dict[str, Any] = {}

        def start_response(status, response_headers, exc_info=None):
            captured["status"] = int(status.split()[0])
            captured["headers"] = {k.lower(): v for k, v in response_headers}

        chunks = b"".join(self.app(environ, start_response))
        return Resp(captured["status"], captured["headers"], json.loads(chunks) if chunks else None)

    def get(self, path, **kw):
        return self.request("GET", path, **kw)

    def post(self, path, body=None, **kw):
        return self.request("POST", path, body, **kw)

    def patch(self, path, body=None, **kw):
        return self.request("PATCH", path, body, **kw)

    def as_customer(self, customer: str) -> Client:
        return Client(self.app, customer)


ITEMS = [{"sku": "A-1", "qty": 2, "unit_price_cents": 1250}]


def new_order(client: Client, items=None, **kw) -> dict:
    resp = client.post("/orders", {"items": items or ITEMS}, **kw)
    assert resp.status == 201, resp.body
    return resp.body


def patch_order(client: Client, order_id: int, body: dict) -> Resp:
    """PATCH with the current ETag when the API provides one."""
    etag = client.get(f"/orders/{order_id}").etag
    return client.patch(f"/orders/{order_id}", body, headers={"If-Match": etag} if etag else {})


def run_threads(jobs, timeout: float = 30.0) -> list:
    """Run callables in threads released together by a barrier; return their results."""
    barrier = threading.Barrier(len(jobs))
    results: list = [None] * len(jobs)

    def wrap(i, job):
        barrier.wait(10)
        try:
            results[i] = job()
        except BaseException as exc:  # noqa: BLE001 - reported to the test
            results[i] = exc

    threads = [threading.Thread(target=wrap, args=(i, j), daemon=True) for i, j in enumerate(jobs)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout)
    assert not any(t.is_alive() for t in threads), "worker threads did not finish"
    return results


@pytest.fixture
def db_path(tmp_path):
    return str(tmp_path / "orders.db")


@pytest.fixture
def client(db_path):
    from orders import create_app

    return Client(create_app(db_path), "c1")
