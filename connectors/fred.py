"""FRED (St. Louis Fed): US and international economic time series (free key)."""

from connectors.base import Connector


class Fred(Connector):
    id = "fred"
    name = "FRED"
    base_url = "https://api.stlouisfed.org/fred"
    key_env = "FRED_API_KEY"
    key_required = True

    def auth_params(self):
        return {"api_key": self.key, "file_type": "json"} if self.key else {}

    def _search(self, query, limit=10):
        data, retrieved = self.request(f"{self.base_url}/series/search", {"search_text": query, "limit": limit})
        return [
            self.record(
                id=s["id"],
                title=s["title"],
                url=f"https://fred.stlouisfed.org/series/{s['id']}",
                retrieved_at=retrieved,
                published_at=(s.get("last_updated") or "")[:10] or None,
                series_id=s["id"],
                unit=s.get("units"),
                data={
                    "frequency": s.get("frequency"),
                    "start": s.get("observation_start"),
                    "end": s.get("observation_end"),
                },
            )
            for s in data["seriess"]
        ]

    def _fetch(self, series_id, limit=12):
        data, retrieved = self.request(
            f"{self.base_url}/series/observations", {"series_id": series_id, "sort_order": "desc", "limit": limit}
        )
        return [
            self.record(
                id=f"{series_id}:{o['date']}",
                title=f"FRED {series_id}",
                retrieved_at=retrieved,
                url=f"https://fred.stlouisfed.org/series/{series_id}",
                series_id=series_id,
                value=float(o["value"]) if o["value"] != "." else None,
                period=o["date"],
            )
            for o in data["observations"]
        ]
