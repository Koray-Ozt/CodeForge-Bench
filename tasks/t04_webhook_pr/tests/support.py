from __future__ import annotations

from hooks import Response


class FakeTransport:
    """Scripted transport: returns/raises each outcome in turn, repeating the last one."""

    def __init__(self, *outcomes: Response | Exception) -> None:
        self._outcomes = list(outcomes)
        self.calls: list[dict] = []

    def __call__(self, url, body, headers, timeout):
        self.calls.append({"url": url, "body": body, "headers": dict(headers)})
        index = min(len(self.calls), len(self._outcomes)) - 1
        outcome = self._outcomes[index]
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


def ok(status: int = 200) -> Response:
    return Response(status)


class Sleeps:
    def __init__(self) -> None:
        self.delays: list[float] = []

    def __call__(self, seconds: float) -> None:
        self.delays.append(seconds)
