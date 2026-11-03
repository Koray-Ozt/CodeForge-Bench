"""WSGI application: routing, JSON handling and error mapping."""

from __future__ import annotations

import json
import re
from http import HTTPStatus
from typing import Any

from . import service
from .db import connect, init_db
from .errors import ApiError

MAX_BODY_BYTES = 64 * 1024
ORDER_PATH = re.compile(r"^/orders/(\d+)$")

Response = tuple[int, list[tuple[str, str]], Any]


def _read_json(environ: dict[str, Any]) -> dict[str, Any]:
    try:
        length = int(environ.get("CONTENT_LENGTH") or 0)
    except ValueError:
        raise ApiError(400, "invalid_length") from None
    if length > MAX_BODY_BYTES:
        raise ApiError(413, "body_too_large")
    raw = environ["wsgi.input"].read(length) if length else b""
    try:
        data = json.loads(raw or b"{}")
    except ValueError:
        raise ApiError(400, "invalid_json") from None
    if not isinstance(data, dict):
        raise ApiError(400, "invalid_json", "body must be a JSON object")
    return data


def _customer(environ: dict[str, Any]) -> str:
    customer = environ.get("HTTP_X_CUSTOMER_ID", "").strip()
    if not customer:
        raise ApiError(401, "missing_customer", "X-Customer-Id header is required")
    return customer


def _route(db_path: str, environ: dict[str, Any]) -> Response:
    method, path = environ["REQUEST_METHOD"], environ["PATH_INFO"]
    customer = _customer(environ)
    with connect(db_path) as conn:
        if path == "/orders":
            if method == "POST":
                return 201, [], service.create_order(conn, customer, _read_json(environ))
            if method == "GET":
                return 200, [], {"items": service.list_orders(conn, customer)}
            raise ApiError(405, "method_not_allowed")
        match = ORDER_PATH.match(path)
        if match:
            order_id = int(match.group(1))
            if method == "GET":
                return 200, [], service.get_order(conn, customer, order_id)
            if method == "PATCH":
                body = _read_json(environ)
                return 200, [], service.update_order(conn, customer, order_id, body)
            raise ApiError(405, "method_not_allowed")
    raise ApiError(404, "not_found", f"no route for {path}")


def create_app(db_path: str):
    init_db(db_path)

    def app(environ, start_response):
        try:
            status, headers, payload = _route(db_path, environ)
        except ApiError as exc:
            status, headers = exc.status, []
            payload = {"error": exc.code, "message": exc.message}
        except Exception:  # noqa: BLE001 - last-resort 500, details stay in server logs
            status, headers = 500, []
            payload = {"error": "internal_error"}
        body = json.dumps(payload).encode()
        phrase = HTTPStatus(status).phrase
        start_response(
            f"{status} {phrase}",
            [("Content-Type", "application/json"), ("Content-Length", str(len(body))), *headers],
        )
        return [body]

    return app
