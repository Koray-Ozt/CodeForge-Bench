# Add signed webhook delivery with retries

Adds `hooks.deliver()` for outgoing webhooks plus `hooks.sign()` / `hooks.verify()`.

## What it does

- Serializes the payload as compact, key-sorted JSON and signs it with HMAC-SHA256.
  Signature and timestamp travel in `X-Webhook-Signature` / `X-Webhook-Timestamp`.
- `verify()` is for our own receivers (the partner portal). It must reject replays, so it
  takes a tolerance window (default 5 minutes).
- Retries transient failures with exponential backoff, gives up after `max_attempts`.
- Every delivery carries a unique `X-Webhook-Id` so receivers can deduplicate retries.
- Raises `DeliveryFailed` when delivery does not succeed.

## Testing

Manually against the staging receiver: happy path, a 503, and a dropped connection all
behaved. Unit tests will follow in a separate PR.

## Notes for reviewers

Left a `noqa` on the default `headers` argument, ruff was being picky.
