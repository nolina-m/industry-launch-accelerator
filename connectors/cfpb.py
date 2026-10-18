"""CFPB Consumer Complaint Database: complaint themes in financial services (no key)."""

from connectors.base import Connector


class Cfpb(Connector):
    id = "cfpb"
    name = "CFPB Consumer Complaints"
    base_url = "https://www.consumerfinance.gov/data-research/consumer-complaints/search/api/v1/"

    def _search(self, query, product=None, since=None, limit=10):
        params = {"search_term": query, "size": limit, "sort": "created_date_desc"}
        if product:
            params["product"] = product
        if since:
            params["date_received_min"] = since
        data, retrieved = self.request(self.base_url, params)
        total = data["hits"]["total"]["value"]
        out = [
            self.record(
                id=f"total:{query}",
                title=f"CFPB complaints mentioning '{query}'",
                url="https://www.consumerfinance.gov/data-research/consumer-complaints/",
                retrieved_at=retrieved,
                series_id=f"complaints?search_term={query}",
                value=total,
                unit="complaints",
            )
        ]
        for bucket in data.get("aggregations", {}).get("issue", {}).get("issue", {}).get("buckets", [])[:10]:
            out.append(
                self.record(
                    id=f"issue:{bucket['key']}",
                    title=f"Issue: {bucket['key']}",
                    url="https://www.consumerfinance.gov/data-research/consumer-complaints/",
                    retrieved_at=retrieved,
                    series_id="aggregations.issue",
                    value=bucket["doc_count"],
                    unit="complaints",
                )
            )
        for hit in data["hits"]["hits"]:
            s = hit["_source"]
            out.append(
                self.record(
                    id=str(s["complaint_id"]),
                    title=f"{s.get('product')}: {s.get('issue')}",
                    url=f"https://www.consumerfinance.gov/data-research/consumer-complaints/search/detail/{s['complaint_id']}",
                    retrieved_at=retrieved,
                    published_at=(s.get("date_received") or "")[:10] or None,
                    data={"company": s.get("company"), "state": s.get("state"), "response": s.get("company_response")},
                )
            )
        return out
