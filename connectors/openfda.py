"""openFDA: device and drug recalls, adverse events, approvals (no key; OPENFDA_API_KEY raises limits)."""

from connectors.base import Connector


class OpenFda(Connector):
    id = "openfda"
    name = "openFDA"
    base_url = "https://api.fda.gov"
    key_env = "OPENFDA_API_KEY"

    def auth_params(self):
        return {"api_key": self.key} if self.key else {}

    def _search(self, query, endpoint="device/recall", limit=20):
        """query uses openFDA syntax, e.g. "reason_for_recall:software".

        endpoint: device/recall, drug/enforcement, device/event, ...
        """
        data, retrieved = self.request(
            f"{self.base_url}/{endpoint}.json", {"search": query, "limit": limit}, accept_status=(200, 404)
        )
        if "error" in data:  # openFDA answers 404 when nothing matches
            if data["error"].get("code") == "NOT_FOUND":
                return []
            from connectors.base import ConnectorError

            raise ConnectorError(f"openFDA: {data['error'].get('message', 'error')}")
        total = data["meta"]["results"]["total"]
        out = [
            self.record(
                id=f"{endpoint}:{query}:total",
                title=f"openFDA {endpoint} matching '{query}'",
                url=f"https://open.fda.gov/apis/{endpoint}/",
                retrieved_at=retrieved,
                published_at=data["meta"].get("last_updated"),
                series_id=f"{endpoint}?search={query}",
                value=total,
                unit="records",
            )
        ]
        for r in data["results"]:
            rid = r.get("res_event_number") or r.get("recall_number") or r.get("cfres_id") or r.get("safetyreportid")
            out.append(
                self.record(
                    id=str(rid),
                    title=(r.get("product_description") or r.get("reason_for_recall") or "")[:160],
                    url=f"https://open.fda.gov/apis/{endpoint}/",
                    retrieved_at=retrieved,
                    published_at=r.get("event_date_posted") or r.get("report_date"),
                    summary=r.get("reason_for_recall", ""),
                    data={"firm": r.get("recalling_firm"), "status": r.get("recall_status")},
                )
            )
        return out
