"""Data connectors with recorded responses (FR-API-01..05, FR-TST-02).

Each connector has a recorded response in fixtures/<id>.json: the real API's shape
with placeholder values. No test touches the network.
"""

import json
from pathlib import Path

import pytest

from connectors import registry
from connectors.base import Connector, Response

FIXTURES = Path(__file__).parent / "fixtures"
ENV_ALL_KEYS = {
    "ILA_CONTACT_EMAIL": "tests@example.org",
    **{e["key_env"]: "test-key" for e in registry.entries().values() if e.get("key_env")},
}


class RecordedTransport:
    """Answers each request with the first recorded response whose `match` is in the URL."""

    def __init__(self, responses):
        self.responses = responses
        self.calls = []

    def __call__(self, method, url, params, headers, body, timeout):
        self.calls.append({"method": method, "url": url, "params": params, "headers": headers, "body": body})
        for r in self.responses:
            if r["match"] in url:
                return Response(r["status"], json.dumps(r["body"]))
        return Response(404, "not recorded")


def load_fixture(cid):
    return json.loads((FIXTURES / f"{cid}.json").read_text())


def make(cid, transport, env=ENV_ALL_KEYS, **kw):
    return registry.get(cid, transport=transport, env=env, sleep=lambda s: None, **kw)


# ------------------------------------------------------------------ registry
def test_every_registered_connector_has_a_recorded_response():
    assert sorted(registry.entries()) == sorted(p.stem for p in FIXTURES.glob("*.json"))


@pytest.mark.parametrize("cid", sorted(registry.entries()))
def test_registry_matches_the_connector_class(cid):
    entry, cls = registry.entries()[cid], registry.connector_class(cid)
    assert cls.id == cid
    assert cls.key_env == entry["key_env"]
    assert cls.key_required == (entry["access"] == "key")
    assert (entry["access"] == "optional_key") == (cls.key_env is not None and not cls.key_required)
    assert entry["docs_url"].startswith("https://")
    if entry["access"] != "none":
        assert entry["signup_url"].startswith("https://")


# ------------------------------------------------------------------ recorded responses
@pytest.mark.parametrize("cid", sorted(registry.entries()))
def test_connector_reads_its_recorded_response(cid, tmp_path):
    fx = load_fixture(cid)
    transport = RecordedTransport(fx["responses"])
    c = make(cid, transport, cache_dir=tmp_path)
    records = getattr(c, fx["call"]["method"])(*fx["call"]["args"], **fx["call"]["kwargs"])
    assert c.last_error is None
    assert len(records) == fx["expect"]["count"]
    first = records[0].to_dict()
    for field, value in fx["expect"]["first"].items():
        assert first[field] == value, f"{cid}: {field}"
    for rec in records:  # FR-API-04: every result says where and when it came from
        assert rec.connector == cid and rec.retrieved_at and rec.url
    assert transport.calls[0]["headers"]["User-Agent"].startswith("IndustryLaunchAccelerator/")


# ------------------------------------------------------------------ degrading gracefully
@pytest.mark.parametrize("cid", [c for c, e in registry.entries().items() if e["access"] == "key"])
def test_missing_key_means_off_and_fails_soft(cid):
    transport = RecordedTransport([])
    c = make(cid, transport, env={})
    ok, reason = c.available()
    assert not ok and c.key_env in reason
    fx = load_fixture(cid)
    assert getattr(c, fx["call"]["method"])(*fx["call"]["args"], **fx["call"]["kwargs"]) == []
    assert c.key_env in c.last_error
    assert transport.calls == []  # never even tried


def test_optional_key_sources_work_without_a_key():
    for cid, e in registry.entries().items():
        if e["access"] in ("none", "optional_key") and cid != "sec-edgar":
            assert make(cid, RecordedTransport([]), env={}).available()[0], cid


def test_sec_needs_a_contact_email():
    c = make("sec-edgar", RecordedTransport([]), env={})
    ok, reason = c.available()
    assert not ok and "ILA_CONTACT_EMAIL" in reason
    c = make("sec-edgar", RecordedTransport([]), env={"ILA_CONTACT_EMAIL": "me@example.org"})
    assert c.headers()["User-Agent"].endswith("me@example.org")
    assert "http" not in c.headers()["User-Agent"]  # SEC refuses agents containing a URL


@pytest.mark.parametrize("status,expected", [(500, "HTTP 500"), (429, "rate-limiting"), (403, "refused")])
def test_http_errors_fail_soft(status, expected):
    c = make("worldbank", RecordedTransport([{"match": "worldbank", "status": status, "body": {}}]))
    assert c.fetch("NY.GDP.MKTP.CD") == []
    assert expected in c.last_error


def test_network_failure_fails_soft():
    def broken(*args):
        raise ConnectionError("offline")

    c = make("hackernews", broken)
    assert c.search("x") == []
    assert "could not reach" in c.last_error


def test_unexpected_response_shape_fails_soft():
    c = make("hackernews", RecordedTransport([{"match": "algolia", "status": 200, "body": {"surprise": True}}]))
    assert c.search("x") == []
    assert "unexpected" in c.last_error


def test_unsupported_method_fails_soft():
    c = make("arbeitnow", RecordedTransport([]))
    assert c.fetch("x") == []
    assert "does not support" in c.last_error


# ------------------------------------------------------------------ cache and rate limits
def test_responses_are_cached_with_retrieval_time_and_without_keys(tmp_path):
    fx = load_fixture("fred")
    transport = RecordedTransport(fx["responses"])
    c = make("fred", transport, cache_dir=tmp_path)
    first = c.fetch("PLACEHOLDER")
    cached = list((tmp_path / "fred").glob("*.json"))
    assert len(cached) == 1
    stored = json.loads(cached[0].read_text())
    assert stored["retrieved_at"] == first[0].retrieved_at
    assert "test-key" not in cached[0].read_text()
    second = c.fetch("PLACEHOLDER")
    assert len(transport.calls) == 1 and c.last_from_cache  # served from cache
    assert [r.value for r in second] == [r.value for r in first]


def test_refresh_bypasses_cache_and_keeps_the_previous_copy(tmp_path):
    fx = load_fixture("fred")
    make("fred", RecordedTransport(fx["responses"]), cache_dir=tmp_path).fetch("PLACEHOLDER")
    transport = RecordedTransport(fx["responses"])
    make("fred", transport, cache_dir=tmp_path, use_cache=False).fetch("PLACEHOLDER")
    assert len(transport.calls) == 1
    assert len(list((tmp_path / "fred").glob("*.prev.json"))) == 1


def test_rate_limit_spacing_is_respected():
    waits = []
    fx = load_fixture("gdelt")
    c = registry.get("gdelt", transport=RecordedTransport(fx["responses"]), env={}, sleep=waits.append)
    Connector._last_call.pop("gdelt", None)
    c.search("a")
    c.search("b")
    assert waits and waits[-1] > 4  # GDELT asks for one request every 5 seconds


def test_key_goes_in_the_request_not_the_cache_key(tmp_path):
    fx = load_fixture("regulations-gov")
    transport = RecordedTransport(fx["responses"])
    make("regulations-gov", transport, cache_dir=tmp_path).search("placeholder")
    assert transport.calls[0]["params"]["api_key"] == "test-key"


def test_openfda_no_matches_is_an_empty_result_not_an_error():
    body = {"error": {"code": "NOT_FOUND", "message": "No matches found!"}}
    c = make("openfda", RecordedTransport([{"match": "api.fda.gov", "status": 404, "body": body}]))
    assert c.search("reason_for_recall:nothing") == []
    assert c.last_error is None


def test_check_reports_ready_needs_setup_and_unreachable():
    from scripts.connectors.check import check

    def down(*args):
        raise ConnectionError("offline")

    rows = {r["id"]: r for r in check(env={}, transport=down)}
    assert rows["fred"]["status"] == "needs setup" and "fredaccount" in rows["fred"]["note"]
    assert rows["worldbank"]["status"] == "unreachable"
    assert rows["sec-edgar"]["status"] == "needs setup"
    offline = {r["id"]: r for r in check(offline=True, env={"FRED_API_KEY": "k"})}
    assert offline["fred"]["status"] == "ready" and offline["worldbank"]["status"] == "ready"


def test_query_tool_registers_sources_with_series_and_connector(tmp_path, monkeypatch, capsys):
    from scripts.connectors import query
    from scripts.sources import load
    from scripts.state.launch_state import LaunchState

    LaunchState.create(tmp_path / "q", "q")
    fx = load_fixture("bls")
    monkeypatch.setattr(query, "LAUNCHES_DIR", tmp_path)
    monkeypatch.setattr(query, "load_env", lambda: {})
    real_get = registry.get
    monkeypatch.setattr(query.registry, "get",
                        lambda cid, **kw: real_get(cid, **{**kw, "transport": RecordedTransport(fx["responses"]),
                                                           "sleep": lambda s: None}))
    assert query.main(["q", "bls", "fetch", "CES0000000001", "--opt", "limit=1", "--register"]) == 0
    out = capsys.readouterr().out
    assert "series: CES0000000001" in out and "cite as [S1]" in out
    src = load(tmp_path / "q")["sources"][0]
    assert src["connector"] == "bls" and src["tier"] == 1 and "CES0000000001: 1234.5" in src["excerpt"]
    assert list((tmp_path / "q" / "research" / "cache" / "bls").glob("*.json"))


def test_query_tool_reports_unavailable_source_and_continues(tmp_path, monkeypatch, capsys):
    from scripts.connectors import query
    from scripts.state.launch_state import LaunchState

    LaunchState.create(tmp_path / "q", "q")
    monkeypatch.setattr(query, "LAUNCHES_DIR", tmp_path)
    monkeypatch.setattr(query, "load_env", lambda: {})
    assert query.main(["q", "fred", "fetch", "GDP"]) == 0
    assert "not available" in capsys.readouterr().out
