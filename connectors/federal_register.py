"""Federal Register: US rules, proposed rules and notices (no key)."""

from connectors.base import Connector


class FederalRegister(Connector):
    id = "federal-register"
    name = "Federal Register"
    base_url = "https://www.federalregister.gov/api/v1"

    def _doc(self, d, retrieved):
        return self.record(
            id=d["document_number"],
            title=d["title"],
            url=d["html_url"],
            retrieved_at=retrieved,
            published_at=d.get("publication_date"),
            series_id=f"FR:{d['document_number']}",
            summary=d.get("abstract") or "",
            data={
                "type": d.get("type"),
                "agencies": [a.get("name") for a in d.get("agencies", [])],
                "pdf_url": d.get("pdf_url"),
            },
        )

    def _search(self, query, since=None, doc_type=None, agency=None, limit=20):
        """doc_type: RULE, PRORULE (proposed rule) or NOTICE. agency: an agency slug."""
        params = {"conditions[term]": query, "per_page": limit, "order": "newest"}
        if since:
            params["conditions[publication_date][gte]"] = since
        if doc_type:
            params["conditions[type][]"] = doc_type
        if agency:
            params["conditions[agencies][]"] = agency
        data, retrieved = self.request(f"{self.base_url}/documents.json", params)
        return [self._doc(d, retrieved) for d in data.get("results", [])]

    def _fetch(self, document_number):
        data, retrieved = self.request(f"{self.base_url}/documents/{document_number}.json")
        return [self._doc(data, retrieved)]
