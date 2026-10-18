"""CMS Provider Data Catalog: Medicare datasets on hospitals and other providers (no key)."""

from connectors.base import Connector


class Cms(Connector):
    id = "cms"
    name = "CMS Provider Data"
    base_url = "https://data.cms.gov/provider-data/api/1"
    min_interval = 1.0

    def _search(self, query, limit=10):
        data, retrieved = self.request(f"{self.base_url}/search", {"fulltext": query, "page-size": limit})
        results = data.get("results", {})
        items = results.values() if isinstance(results, dict) else results
        return [
            self.record(
                id=d["identifier"],
                title=d["title"],
                url=d.get("landingPage", ""),
                retrieved_at=retrieved,
                published_at=d.get("modified"),
                summary=d.get("description", ""),
                series_id=f"CMS:{d['identifier']}",
                data={"theme": d.get("theme"), "keyword": d.get("keyword")},
            )
            for d in items
        ]
