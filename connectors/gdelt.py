"""GDELT DOC 2.0: global news coverage, mainly for refresh (no key; one request every 5 seconds)."""

from connectors.base import Connector


class Gdelt(Connector):
    id = "gdelt"
    name = "GDELT"
    base_url = "https://api.gdeltproject.org/api/v2/doc/doc"
    min_interval = 5.5

    def _search(self, query, timespan="3months", limit=25):
        data, retrieved = self.request(
            self.base_url,
            {
                "query": query,
                "mode": "artlist",
                "format": "json",
                "maxrecords": limit,
                "timespan": timespan,
                "sort": "datedesc",
            },
        )
        if not isinstance(data, dict):
            return []  # GDELT answers with plain text when nothing matches
        out = []
        for a in data.get("articles", []):
            seen = a.get("seendate", "")
            date = f"{seen[:4]}-{seen[4:6]}-{seen[6:8]}" if len(seen) >= 8 else None
            out.append(
                self.record(
                    id=a["url"],
                    title=a.get("title", ""),
                    url=a["url"],
                    retrieved_at=retrieved,
                    published_at=date,
                    data={"domain": a.get("domain"), "language": a.get("language"), "country": a.get("sourcecountry")},
                )
            )
        return out
