"""Regulations.gov: US federal dockets, rules and public comments (free api.data.gov key)."""

from connectors.base import Connector


class RegulationsGov(Connector):
    id = "regulations-gov"
    name = "Regulations.gov"
    base_url = "https://api.regulations.gov/v4"
    key_env = "REGULATIONS_GOV_API_KEY"
    key_required = True

    def auth_params(self):
        return {"api_key": self.key} if self.key else {}

    def _search(self, query, since=None, doc_type=None, limit=20):
        """doc_type: Rule, Proposed Rule, Notice, Supporting & Related Material, Other."""
        params = {"filter[searchTerm]": query, "page[size]": max(5, limit), "sort": "-postedDate"}
        if since:
            params["filter[postedDate][ge]"] = since
        if doc_type:
            params["filter[documentType]"] = doc_type
        data, retrieved = self.request(f"{self.base_url}/documents", params)
        return [
            self.record(
                id=d["id"],
                title=d["attributes"].get("title", ""),
                retrieved_at=retrieved,
                url=f"https://www.regulations.gov/document/{d['id']}",
                published_at=(d["attributes"].get("postedDate") or "")[:10] or None,
                series_id=f"docket:{d['attributes'].get('docketId')}",
                data={
                    "agency": d["attributes"].get("agencyId"),
                    "type": d["attributes"].get("documentType"),
                    "open_for_comment": d["attributes"].get("openForComment"),
                },
            )
            for d in data["data"][:limit]
        ]
