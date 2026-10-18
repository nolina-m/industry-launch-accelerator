"""SAM.gov Opportunities: US federal contract opportunities (free key from a SAM.gov account)."""

from datetime import date, timedelta

from connectors.base import Connector


class SamGov(Connector):
    id = "sam-gov"
    name = "SAM.gov"
    base_url = "https://api.sam.gov/opportunities/v2/search"
    key_env = "SAM_GOV_API_KEY"
    key_required = True
    min_interval = 2.0

    def auth_params(self):
        return {"api_key": self.key} if self.key else {}

    def _search(self, query, days=180, naics=None, limit=25):
        """Opportunities with the query in the title, posted in the last `days` days (max 365)."""
        end = date.today()
        start = end - timedelta(days=min(days, 364))
        params = {
            "title": query,
            "postedFrom": start.strftime("%m/%d/%Y"),
            "postedTo": end.strftime("%m/%d/%Y"),
            "limit": limit,
        }
        if naics:
            params["ncode"] = naics
        data, retrieved = self.request(self.base_url, params)
        return [
            self.record(
                id=o["noticeId"],
                title=o.get("title", ""),
                retrieved_at=retrieved,
                url=o.get("uiLink") or f"https://sam.gov/opp/{o['noticeId']}/view",
                published_at=o.get("postedDate"),
                series_id=f"notice:{o.get('solicitationNumber')}",
                data={
                    "agency": o.get("fullParentPathName"),
                    "type": o.get("type"),
                    "naics": o.get("naicsCode"),
                    "deadline": o.get("responseDeadLine"),
                },
            )
            for o in data.get("opportunitiesData", [])
        ]
