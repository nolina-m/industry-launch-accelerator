"""USAspending: US federal contract and grant awards (no key)."""

from connectors.base import Connector

FIELDS = ["Award ID", "Recipient Name", "Award Amount", "Description", "Awarding Agency", "Start Date"]


class UsaSpending(Connector):
    id = "usaspending"
    name = "USAspending"
    base_url = "https://api.usaspending.gov/api/v2"

    def _search(self, query, since=None, until=None, award_types=("A", "B", "C", "D"), limit=20):
        filters = {"keywords": [query], "award_type_codes": list(award_types)}
        if since:
            filters["time_period"] = [{"start_date": since, "end_date": until or "2100-01-01"}]
        body = {"filters": filters, "fields": FIELDS, "limit": limit, "sort": "Award Amount", "order": "desc"}
        data, retrieved = self.request(f"{self.base_url}/search/spending_by_award/", method="POST", body=body)
        return [
            self.record(
                id=a["Award ID"],
                title=f"{a['Recipient Name']}: {a.get('Description') or ''}"[:200],
                url=f"https://www.usaspending.gov/award/{a.get('generated_internal_id', '')}",
                retrieved_at=retrieved,
                published_at=a.get("Start Date"),
                series_id="Award Amount",
                value=a.get("Award Amount"),
                unit="USD",
                data={"agency": a.get("Awarding Agency"), "recipient": a.get("Recipient Name")},
            )
            for a in data["results"]
        ]
