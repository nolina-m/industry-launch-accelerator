# Adding a data source

A data source takes three things (FR-API-05): **one module**, **one test with a recorded response**, and **one registry row**. You'll need basic Python. If you just want to suggest a source, open an issue with the "New data source" template instead.

## Before you start

Check the source's terms. It must:
- be free to use for business purposes (product marketing is business use);
- allow automated access through an API;
- need either no key, or a key anyone can get for free.

Paid sources and scraping are out of scope.

## 1. The module: `connectors/<name>.py`

Subclass `Connector` and implement `_search` and/or `_fetch`. Use `self.request()` for every call: it adds the User-Agent and the key, respects the rate limit, caches the response, and turns failures into a soft error. Return a list of `Record`s.

```python
"""Example Source: what it's for (no key)."""

from connectors.base import Connector


class ExampleSource(Connector):
    id = "example-source"
    name = "Example Source"
    base_url = "https://api.example.org/v1"
    key_env = None          # or "EXAMPLE_API_KEY"
    key_required = False    # True: off until the key is set
    min_interval = 1.0      # seconds between calls

    def _search(self, query, limit=20):
        data, retrieved = self.request(f"{self.base_url}/search", {"q": query, "limit": limit})
        return [self.record(id=item["id"], title=item["title"], url=item["url"], retrieved_at=retrieved,
                            published_at=item.get("date"), series_id=item.get("series"),
                            value=item.get("value"), unit=item.get("unit"))
                for item in data["results"]]
```

If the key goes in a query parameter, override `auth_params()`. If it goes in a header, override `headers()`. See `connectors/fred.py` and `connectors/currents.py` for examples.

Every `Record` needs a `url` and a `retrieved_at`. Numbers also need a `series_id` and a `period`, so they can be traced (FR-API-04).

## 2. The test: `tests/connectors/fixtures/<id>.json`

Save one response in the API's real shape, with **placeholder values**: no real companies or people. Then say how to call the connector and what you expect back:

```json
{
  "connector": "example-source",
  "call": {"method": "search", "args": ["placeholder"], "kwargs": {"limit": 1}},
  "expect": {"count": 1, "first": {"title": "Placeholder title"}},
  "responses": [
    {"match": "/search", "status": 200, "body": {"results": [
      {"id": "1", "title": "Placeholder title", "url": "https://example.org/1"}]}}
  ]
}
```

`tests/connectors/test_connectors.py` picks it up automatically. It also checks that missing keys, errors and network failures all fail soft.

## 3. The registry row: `connectors/registry.yaml`

```yaml
  - {id: example-source, name: Example Source, class: "connectors.example_source:ExampleSource", tier: 1,
     category: economy, access: none, key_env: null, signup_url: null,
     docs_url: "https://example.org/docs", rate_limit: "see docs", used_for: "What it's good for"}
```

- `tier`: 1 for primary sources (government, regulators, filings, official data); 2 for reputable press and public analyst summaries; 3 for aggregators, forums and reviews.
- `access`: `none`, `optional_key` or `key`.

If it needs a key, add a commented line to `.env.example` with the sign-up link. Add a probe to `PROBES` in `scripts/connectors/check.py`. Then add the source to the table in `docs/data-sources.md`, and to the `connectors` list of any industry pack it suits.

## 4. Check

```
.venv/bin/python -m pytest tests/connectors
.venv/bin/python scripts/connectors/check.py
```
