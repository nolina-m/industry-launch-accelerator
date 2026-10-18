"""Wikipedia: background on companies, technologies and industries (no key). Tier 3: verify facts elsewhere."""

from urllib.parse import quote

from connectors.base import Connector


class Wikipedia(Connector):
    id = "wikipedia"
    name = "Wikipedia"
    base_url = "https://en.wikipedia.org"
    min_interval = 0.2

    def _search(self, query, limit=5):
        data, retrieved = self.request(f"{self.base_url}/w/rest.php/v1/search/page", {"q": query, "limit": limit})
        return [
            self.record(
                id=str(p["id"]),
                title=p["title"],
                url=f"{self.base_url}/wiki/{quote(p['key'])}",
                retrieved_at=retrieved,
                summary=p.get("description") or "",
                data={"key": p["key"]},
            )
            for p in data["pages"]
        ]

    def _fetch(self, title):
        data, retrieved = self.request(f"{self.base_url}/api/rest_v1/page/summary/{quote(title.replace(' ', '_'))}")
        return [
            self.record(
                id=str(data.get("pageid")),
                title=data["title"],
                url=data["content_urls"]["desktop"]["page"],
                retrieved_at=retrieved,
                published_at=(data.get("timestamp") or "")[:10] or None,
                summary=data.get("extract", ""),
                data={"revision": data.get("revision"), "description": data.get("description")},
            )
        ]
