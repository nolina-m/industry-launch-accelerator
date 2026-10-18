"""Hacker News (Algolia search API): technology community discussion (no key). Tier 3."""

from connectors.base import Connector


class HackerNews(Connector):
    id = "hackernews"
    name = "Hacker News"
    base_url = "https://hn.algolia.com/api/v1"

    def _search(self, query, since=None, limit=20):
        params = {"query": query, "tags": "story", "hitsPerPage": limit}
        endpoint = "search_by_date" if since else "search"
        if since:
            from datetime import datetime, timezone

            ts = int(datetime.fromisoformat(since).replace(tzinfo=timezone.utc).timestamp())
            params["numericFilters"] = f"created_at_i>{ts}"
        data, retrieved = self.request(f"{self.base_url}/{endpoint}", params)
        return [
            self.record(
                id=h["objectID"],
                title=h.get("title") or "",
                retrieved_at=retrieved,
                url=h.get("url") or f"https://news.ycombinator.com/item?id={h['objectID']}",
                published_at=(h.get("created_at") or "")[:10] or None,
                series_id="points",
                value=h.get("points"),
                unit="points",
                data={
                    "comments": h.get("num_comments"),
                    "discussion": f"https://news.ycombinator.com/item?id={h['objectID']}",
                },
            )
            for h in data["hits"]
        ]
