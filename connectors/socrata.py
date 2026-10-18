"""Government open-data portals built on Socrata: HealthData.gov, FCC, US DOT (no key).

search() finds datasets on the portal; fetch("<dataset id>") returns the first rows of one.
"""

from connectors.base import Connector


class SocrataPortal(Connector):
    domains: tuple[str, ...] = ()

    def _search(self, query, limit=10):
        params = {"domains": ",".join(self.domains), "q": query, "limit": limit}
        data, retrieved = self.request("https://api.us.socrata.com/api/catalog/v1", params)
        return [
            self.record(
                id=r["resource"]["id"],
                title=r["resource"]["name"],
                url=r.get("permalink") or r["link"],
                retrieved_at=retrieved,
                published_at=(r["resource"].get("data_updated_at") or "")[:10] or None,
                summary=(r["resource"].get("description") or "")[:500],
                series_id=f"{r['metadata']['domain']}/{r['resource']['id']}",
                data={"domain": r["metadata"]["domain"], "license": r["metadata"].get("license")},
            )
            for r in data["results"]
        ]

    def _fetch(self, dataset_id, limit=50, where=None):
        domain = self.domains[0]
        if "/" in dataset_id:
            domain, dataset_id = dataset_id.split("/", 1)
        params = {"$limit": limit}
        if where:
            params["$where"] = where
        rows, retrieved = self.request(f"https://{domain}/resource/{dataset_id}.json", params)
        return [
            self.record(
                id=f"{dataset_id}:{i}",
                title=f"{domain}/{dataset_id} row {i + 1}",
                url=f"https://{domain}/d/{dataset_id}",
                retrieved_at=retrieved,
                series_id=f"{domain}/{dataset_id}",
                data=row,
            )
            for i, row in enumerate(rows)
        ]


class HealthData(SocrataPortal):
    id = "healthdata"
    name = "HealthData.gov"
    domains = ("healthdata.gov",)


class Fcc(SocrataPortal):
    id = "fcc"
    name = "FCC Open Data"
    domains = ("opendata.fcc.gov",)


class UsDot(SocrataPortal):
    id = "us-dot"
    name = "US DOT Open Data"
    domains = ("data.transportation.gov", "data.bts.gov")
