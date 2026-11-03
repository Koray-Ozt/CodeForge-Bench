# Review notes and fix rationale

The PR works on the happy path, which is why staging looked fine. Every defect below only
shows up on a failure path, under attack, or on the second call.

| ID | Where | Category | Defect | Impact | Fix |
|---|---|---|---|---|---|
| D1 | `signing.py:30` | security | `signature == expected` | Timing side channel on signature checking | `hmac.compare_digest` on **bytes**. Passing `str` raises `TypeError` for non-ASCII input, turning a bad header into a 500 (the `naive_quick_fixes` candidate does exactly this) |
| D2 | `signing.py:29-30` | security | `now` and `tolerance` are accepted but never used | Any captured request can be replayed forever, and the docstring claims otherwise | Reject `abs(now - ts) > tolerance`; boundary inclusive |
| D3 | `signing.py:15` | security | Timestamp is not in the MAC | Even with D2 fixed, an attacker can refresh the timestamp of a captured body | Sign `"<ts>." + body` |
| D4 | `delivery.py:94-96` | reliability | Every non-2xx is retried | A `400`/`404`/`410` is retried for about a minute per event, 5 times, multiplying load on already-unhappy receivers; `301` is retried as if transient | Retry only network errors, 408/425/429, 5xx; raise immediately otherwise |
| D5 | `delivery.py:91` | correctness | `range(max_attempts + 1)` | `max_attempts=5` makes 6 requests | `range(1, max_attempts + 1)` |
| D6 | `delivery.py:100` | correctness | `2 ** (attempt + 1)` | First wait is 2x `base_delay`; the whole schedule is shifted one step | `2 ** (attempt - 1)` with 1-based attempts |
| D7 | `delivery.py:101` | error-handling | `return None  # type: ignore` | Callers believe delivery succeeded; events are silently lost. The `type: ignore` is the tell | Raise `DeliveryFailed(attempts, last_status, last_error)` |
| D8 | `delivery.py:97-98` | error-handling | `except Exception: pass` | Swallows programming errors (`TypeError`, bad transport) and the cause of the last failure | Catch only `OSError`/`TransportError`, remember the last error |
| D9 | `delivery.py:75,85` | state | `headers={}` default plus `setdefault` | One dict is shared by every call: all deliveries reuse the first `X-Webhook-Id` (receivers dedupe away real events), and the caller's dict is mutated. The `noqa: B006` silenced the linter that would have caught this | `headers: Mapping | None = None`, copy before use |

## Review heuristics that find these

- **Parameters that are accepted but never read** (`now`, `tolerance`): the signature is
  promising something the body does not do.
- **Suppression comments** (`noqa`, `type: ignore`): each one is a place where a tool
  disagreed with the author.
- **Any `except` that does not name what it expects**, and any function whose last line is
  `return None` while the annotation says otherwise.
- **Loop bounds and exponents**: write down the values for `max_attempts=1` and `=2`.
- **Security primitives**: comparison, replay window, and what exactly is covered by the
  MAC.
- **Second call**: for each mutable default or module-level object, ask what the next call
  sees.

## Residual risk

Retry-After headers on 429 are still ignored, and there is no jitter on backoff, so many
deliveries failing together will retry together. Both are product decisions rather than
defects against the PR's own contract.
