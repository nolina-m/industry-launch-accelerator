"""What every data connector shares (§11.2, FR-API-01..04).

A connector wraps one public data source with two optional methods:

    search(query, **filters) -> list[Record]
    fetch(id, **options)     -> list[Record]

Both *fail soft* (FR-API-03): any problem (no key, network down, rate limit,
unexpected response) returns an empty list and sets `last_error`, so research
continues with web search and the gap is noted. Nothing here ever raises to
the caller.

Every response is cached under research/cache/<connector>/ with its retrieval
time, and every Record carries its source, series ID and retrieval date so
numbers can always be traced (FR-API-04).
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# No URL in the User-Agent: SEC EDGAR refuses agents that contain one (checked 2026-10-18).
USER_AGENT = "IndustryLaunchAccelerator/0.1 (open-source launch toolkit)"
TIMEOUT = 45


class ConnectorError(Exception):
    """A problem talking to a source. Caught inside the connector; never reaches the agent."""


@dataclass
class Record:
    """One result from a data source, in a common shape."""

    connector: str
    id: str
    title: str
    url: str
    retrieved_at: str
    published_at: str | None = None
    series_id: str | None = None
    value: Any = None
    unit: str | None = None
    period: str | None = None
    summary: str = ""
    data: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Response:
    status: int
    text: str

    def json(self) -> Any:
        return json.loads(self.text)


# (method, url, params, headers, json_body, timeout) -> Response
Transport = Callable[[str, str, dict, dict, Any, int], Response]


def requests_transport(method: str, url: str, params: dict, headers: dict, body: Any, timeout: int) -> Response:
    import requests

    r = requests.request(method, url, params=params or None, headers=headers, json=body, timeout=timeout)
    return Response(r.status_code, r.text)


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


class Connector:
    # Filled in by each subclass.
    id: str = ""
    name: str = ""
    base_url: str = ""
    key_env: str | None = None  # environment variable holding the key
    key_required: bool = False  # True: off until the key is set. False: key optional (raises limits)
    min_interval: float = 0.5  # seconds between calls, to respect rate limits
    needs_contact: bool = False  # SEC EDGAR asks for a contact email in the User-Agent

    _last_call: dict[str, float] = {}

    def __init__(
        self,
        cache_dir: Path | None = None,
        transport: Transport | None = None,
        env: dict | None = None,
        use_cache: bool = True,
        sleep: Callable[[float], None] = time.sleep,
    ):
        self.cache_dir = cache_dir
        self.transport = transport or requests_transport
        self.env = env if env is not None else os.environ
        self.use_cache = use_cache
        self.sleep = sleep
        self.last_error: str | None = None
        self.last_from_cache = False

    # ------------------------------------------------------------------ availability
    @property
    def key(self) -> str | None:
        value = self.env.get(self.key_env, "").strip() if self.key_env else ""
        return value or None

    def available(self) -> tuple[bool, str]:
        """(usable now?, reason). Sources that need a key are off until it is set."""
        if self.key_required and not self.key:
            return False, f"needs a free access key: add {self.key_env} to your .env file"
        if self.needs_contact and not self.env.get("ILA_CONTACT_EMAIL", "").strip():
            return False, "needs ILA_CONTACT_EMAIL in your .env file (the source asks for a contact address)"
        return True, "ready" + (
            " (no key needed)"
            if not self.key_env
            else " (key set)"
            if self.key
            else " (works without a key; a key raises limits)"
        )

    def headers(self) -> dict:
        ua = USER_AGENT
        contact = self.env.get("ILA_CONTACT_EMAIL", "").strip()
        if contact:
            ua = f"{ua} {contact}"
        return {"User-Agent": ua, "Accept": "application/json"}

    def auth_params(self) -> dict:
        """Query parameters that carry the key. Override for sources that use a header."""
        return {}

    # ------------------------------------------------------------------ HTTP with cache
    def _cache_path(self, method: str, url: str, params: dict, body: Any) -> Path | None:
        if not self.cache_dir:
            return None
        safe = {k: v for k, v in sorted(params.items()) if "key" not in k.lower() and "token" not in k.lower()}
        raw = json.dumps([method, url, safe, body], sort_keys=True, default=str)
        return self.cache_dir / self.id / (hashlib.sha256(raw.encode()).hexdigest()[:20] + ".json")

    def request(
        self,
        url: str,
        params: dict | None = None,
        method: str = "GET",
        body: Any = None,
        accept_status: tuple[int, ...] = (200,),
    ) -> tuple[Any, str]:
        """Return (parsed JSON or text, retrieved_at). Raises ConnectorError on any problem."""
        ok, reason = self.available()
        if not ok:
            raise ConnectorError(reason)
        params = dict(params or {})
        cache = self._cache_path(method, url, params, body)
        if cache and self.use_cache and cache.exists():
            cached = json.loads(cache.read_text(encoding="utf-8"))
            self.last_from_cache = True
            return cached["body"], cached["retrieved_at"]
        self.last_from_cache = False
        wait = self.min_interval - (time.monotonic() - Connector._last_call.get(self.id, 0.0))
        if wait > 0:
            self.sleep(wait)
        try:
            response = self.transport(method, url, {**params, **self.auth_params()}, self.headers(), body, TIMEOUT)
        except Exception as exc:  # network errors of any kind
            raise ConnectorError(f"could not reach {self.name} ({type(exc).__name__})") from exc
        finally:
            Connector._last_call[self.id] = time.monotonic()
        if response.status == 429:
            raise ConnectorError(f"{self.name} is rate-limiting requests; try again later")
        if response.status in (401, 403):
            hint = "; check the access key in .env" if self.key_env else ""
            raise ConnectorError(f"{self.name} refused the request (HTTP {response.status}){hint}")
        if response.status not in accept_status:
            raise ConnectorError(f"{self.name} returned HTTP {response.status}")
        try:
            parsed = response.json()
        except ValueError:
            parsed = response.text
        retrieved = now_iso()
        if cache:
            cache.parent.mkdir(parents=True, exist_ok=True)
            previous = cache.with_suffix(".prev.json")
            if cache.exists():
                cache.replace(previous)  # keep the last run for refresh comparisons
            cache.write_text(
                json.dumps(
                    {
                        "url": url,
                        "params": {k: v for k, v in params.items() if "key" not in k.lower()},
                        "retrieved_at": retrieved,
                        "body": parsed,
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
        return parsed, retrieved

    # ------------------------------------------------------------------ public API
    def search(self, query: str, **filters) -> list[Record]:
        return self._safe(self._search, query, **filters)

    def fetch(self, item_id: str, **options) -> list[Record]:
        return self._safe(self._fetch, item_id, **options)

    def _safe(self, func, *args, **kwargs) -> list[Record]:
        self.last_error = None
        try:
            return func(*args, **kwargs)
        except ConnectorError as exc:
            self.last_error = str(exc)
        except NotImplementedError:
            self.last_error = f"{self.name} does not support this; use the other method"
        except Exception as exc:  # unexpected response shape: never stop the run
            self.last_error = f"{self.name} returned something unexpected ({type(exc).__name__}: {exc})"
        return []

    def _search(self, query: str, **filters) -> list[Record]:
        raise NotImplementedError

    def _fetch(self, item_id: str, **options) -> list[Record]:
        raise NotImplementedError

    def record(self, **kwargs) -> Record:
        return Record(connector=self.id, **kwargs)
