"""FDIC BankFind Suite: US banks, their size and financials (no key)."""

from connectors.base import Connector


class Fdic(Connector):
    id = "fdic"
    name = "FDIC BankFind"
    base_url = "https://api.fdic.gov/banks"

    def _search(self, query="", state=None, active=True, limit=25):
        """query matches the bank name; results sorted by total assets."""
        filters = []
        if state:
            filters.append(f"STALP:{state}")
        if active:
            filters.append("ACTIVE:1")
        params = {
            "limit": limit,
            "sort_by": "ASSET",
            "sort_order": "DESC",
            "fields": "NAME,CERT,ASSET,CITY,STALP,REPDTE,ACTIVE",
        }
        if filters:
            params["filters"] = " AND ".join(filters)
        if query:
            params["search"] = f"NAME:{query}"
        data, retrieved = self.request(f"{self.base_url}/institutions", params)
        out = [
            self.record(
                id="total",
                title="Matching FDIC-insured institutions",
                url="https://banks.data.fdic.gov/",
                retrieved_at=retrieved,
                series_id=f"institutions?{params.get('filters', '')}",
                value=data["meta"]["total"],
                unit="institutions",
            )
        ]
        for item in data["data"]:
            d = item["data"]
            out.append(
                self.record(
                    id=str(d["CERT"]),
                    title=d["NAME"],
                    retrieved_at=retrieved,
                    url=f"https://banks.data.fdic.gov/bankfind-suite/bankfind/details/{d['CERT']}",
                    series_id="ASSET",
                    value=d.get("ASSET"),
                    unit="USD thousands",
                    period=d.get("REPDTE"),
                    data={"city": d.get("CITY"), "state": d.get("STALP")},
                )
            )
        return out
