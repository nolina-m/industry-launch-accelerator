"""NPPES NPI Registry: US healthcare providers and organizations (no key)."""

from connectors.base import Connector


class Nppes(Connector):
    id = "nppes"
    name = "NPPES NPI Registry"
    base_url = "https://npiregistry.cms.hhs.gov/api/"

    def _search(self, query, state=None, city=None, organization=False, limit=50):
        """query is a taxonomy description, e.g. "hospital"; organization=True limits to organizations."""
        params = {"version": "2.1", "taxonomy_description": query, "limit": limit}
        if state:
            params["state"] = state
        if city:
            params["city"] = city
        if organization:
            params["enumeration_type"] = "NPI-2"
        data, retrieved = self.request(self.base_url, params)
        out = []
        for r in data.get("results", []):
            b = r.get("basic", {})
            name = b.get("organization_name") or f"{b.get('first_name', '')} {b.get('last_name', '')}".strip()
            loc = next(
                (a for a in r.get("addresses", []) if a.get("address_purpose") == "LOCATION"),
                (r.get("addresses") or [{}])[0],
            )
            out.append(
                self.record(
                    id=r["number"],
                    title=name,
                    retrieved_at=retrieved,
                    url=f"https://npiregistry.cms.hhs.gov/provider-view/{r['number']}",
                    data={
                        "type": r.get("enumeration_type"),
                        "city": loc.get("city"),
                        "state": loc.get("state"),
                        "taxonomy": [t.get("desc") for t in r.get("taxonomies", [])],
                    },
                )
            )
        meta = self.record(
            id=f"count:{query}:{state or 'US'}",
            title=f"NPI records matching '{query}'",
            url="https://npiregistry.cms.hhs.gov/",
            retrieved_at=retrieved,
            series_id="result_count (capped at the request limit)",
            value=data.get("result_count"),
        )
        return [meta] + out
