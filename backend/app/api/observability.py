"""Bounded, label-only operational metrics and safe alert signals.

No request URL, headers, body, identity, exception text or correlation identifier
enters any metric or log.  Process-local counters are not a durable monitoring sink.
"""

from __future__ import annotations

import logging
from collections import Counter, deque
from threading import Lock
from time import monotonic, perf_counter

from fastapi import Request, Response

_SAFE_METHODS = frozenset({"GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"})
_STATUS_BUCKETS = frozenset({"2xx", "3xx", "4xx", "5xx"})
_SIGNAL_NAMES = frozenset({"login_failure", "forbidden", "rate_limited", "server_error"})
_ALERT_THRESHOLDS = {
    "login_failure": 10,
    "forbidden": 10,
    "rate_limited": 5,
    "server_error": 5,
}
_WINDOW_SECONDS = 60.0
_LATENCY_BOUNDS_MS = (100, 500, 1000, 5000)


class OperationalMetrics:
    """Bounded process-local counters with once-per-window safe alerts."""

    def __init__(self, logger: logging.Logger) -> None:
        self._logger = logger
        self._lock = Lock()
        self._requests: Counter[tuple[str, str]] = Counter()
        self._latency: Counter[str] = Counter()
        self._signals: Counter[str] = Counter()
        self._events: dict[str, deque[float]] = {signal: deque() for signal in _SIGNAL_NAMES}
        self._last_alert: dict[str, float] = {}

    def record(self, method: str, status_code: int, duration_ms: float, *, login_failure: bool = False) -> None:
        safe_method = method if method in _SAFE_METHODS else "OTHER"
        status = f"{status_code // 100}xx" if 200 <= status_code < 600 else "other"
        if status not in _STATUS_BUCKETS:
            status = "other"
        label = next((str(bound) for bound in _LATENCY_BOUNDS_MS if duration_ms <= bound), "over_5000")
        signals: list[str] = []
        if login_failure and status_code in (400, 401, 403, 429):
            signals.append("login_failure")
        if status_code == 403:
            signals.append("forbidden")
        if status_code == 429:
            signals.append("rate_limited")
        if status_code >= 500:
            signals.append("server_error")
        now = monotonic()
        alerts: list[str] = []
        with self._lock:
            self._requests[(safe_method, status)] += 1
            self._latency[label] += 1
            for signal in signals:
                self._signals[signal] += 1
                recent = self._events[signal]
                recent.append(now)
                while recent and now - recent[0] > _WINDOW_SECONDS:
                    recent.popleft()
                if len(recent) >= _ALERT_THRESHOLDS[signal] and (
                    now - self._last_alert.get(signal, float("-inf")) >= _WINDOW_SECONDS
                ):
                    self._last_alert[signal] = now
                    alerts.append(signal)
        for signal in alerts:
            self._logger.warning(
                "operational_alert signal=%s window_seconds=60 threshold=%d",
                signal,
                _ALERT_THRESHOLDS[signal],
            )

    def snapshot(self) -> dict[str, dict[str, int]]:
        """Return an internal-only, PII-free copy. Do not expose as a public route."""
        with self._lock:
            return {
                "request_counts": {f"{method}_{status}": count for (method, status), count in self._requests.items()},
                "latency_buckets_ms": dict(self._latency),
                "signals": dict(self._signals),
            }


async def operational_observability_middleware(request: Request, call_next) -> Response:  # type: ignore[no-untyped-def]
    """Record bounded request outcomes; never inspect request content or URI."""
    started = perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        request.app.state.operational_metrics.record(
            request.method, 500, (perf_counter() - started) * 1000
        )
        raise
    if request.url.path.startswith("/api/v1/"):
        # Only exact static endpoints qualify as login failures. Never log paths.
        login_failure = request.url.path in {
            "/api/v1/account-access/request",
            "/api/v1/account-access/verify",
        }
        request.app.state.operational_metrics.record(
            request.method,
            response.status_code,
            (perf_counter() - started) * 1000,
            login_failure=login_failure,
        )
    return response
