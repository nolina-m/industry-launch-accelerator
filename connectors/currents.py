"""Currents API: recent news from many publishers (free key; 250 requests a day, 20 results each)."""

from connectors.base import Connector


class Currents(Connector):
    id = "currents"
    name = "Currents API"
    base_url = "https://api.currentsapi.services/v1"
    key_env = "CURRENTS_API_KEY"
    key_required = True

    def headers(self):
        h = super().headers()
        if self.key:
            h["Authorization"] = self.key
        return h

    def _search(self, query, since=None, language="en", limit=20):
        params = {"keywords": query, "language": language, "page_size": min(limit, 20)}
        if since:
            params["start_date"] = f"{since}T00:00:00Z"
        data, retrieved = self.request(f"{self.base_url}/search", params)
        return [
            self.record(
                id=n["id"],
                title=n.get("title", ""),
                url=n["url"],
                retrieved_at=retrieved,
                published_at=(n.get("published") or "")[:10] or None,
                summary=(n.get("description") or "")[:500],
                data={"author": n.get("author"), "category": n.get("category")},
            )
            for n in data.get("news", [])
        ]
