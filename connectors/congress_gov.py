"""Congress.gov: US bills and their status (free api.data.gov key)."""

from connectors.base import Connector


class CongressGov(Connector):
    id = "congress-gov"
    name = "Congress.gov"
    base_url = "https://api.congress.gov/v3"
    key_env = "CONGRESS_GOV_API_KEY"
    key_required = True

    def auth_params(self):
        return {"api_key": self.key, "format": "json"} if self.key else {}

    def _bill(self, b, retrieved):
        bid = f"{b['congress']}-{b['type'].lower()}-{b['number']}"
        action = b.get("latestAction") or {}
        return self.record(
            id=bid,
            title=b.get("title", ""),
            retrieved_at=retrieved,
            url=f"https://www.congress.gov/bill/{b['congress']}th-congress/"
            f"{'house' if b['type'].upper().startswith('H') else 'senate'}-bill/{b['number']}",
            published_at=b.get("introducedDate") or action.get("actionDate"),
            series_id=f"bill:{bid}",
            summary=action.get("text", ""),
            data={"latest_action_date": action.get("actionDate")},
        )

    def _search(self, query, congress=None, limit=20):
        """The API has no keyword search: this lists the most recently updated bills and keeps
        those whose title contains every query word."""
        path = f"{self.base_url}/bill/{congress}" if congress else f"{self.base_url}/bill"
        data, retrieved = self.request(path, {"limit": 250, "sort": "updateDate+desc"})
        words = [w.lower() for w in query.split()]
        bills = [b for b in data.get("bills", []) if all(w in b.get("title", "").lower() for w in words)]
        return [self._bill(b, retrieved) for b in bills[:limit]]

    def _fetch(self, bill_id):
        """bill_id like '119-hr-1234'."""
        congress, bill_type, number = bill_id.split("-")
        data, retrieved = self.request(f"{self.base_url}/bill/{congress}/{bill_type}/{number}")
        return [self._bill(data["bill"], retrieved)]
