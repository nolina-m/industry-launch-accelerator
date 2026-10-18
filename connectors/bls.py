"""Bureau of Labor Statistics: employment, wages and prices by series ID (no key; BLS_API_KEY raises limits)."""

from connectors.base import Connector


class Bls(Connector):
    id = "bls"
    name = "U.S. Bureau of Labor Statistics"
    base_url = "https://api.bls.gov/publicAPI"
    key_env = "BLS_API_KEY"
    min_interval = 1.0

    def _fetch(self, series_id, limit=12):
        """series_id like CES6562000001 (health care employment). Several: comma-separated."""
        ids = [s.strip() for s in series_id.split(",") if s.strip()]
        version = "v2" if self.key else "v1"
        body = {"seriesid": ids}
        if self.key:
            body["registrationkey"] = self.key
        data, retrieved = self.request(f"{self.base_url}/{version}/timeseries/data/", method="POST", body=body)
        if data.get("status") != "REQUEST_SUCCEEDED":
            from connectors.base import ConnectorError

            raise ConnectorError("BLS: " + "; ".join(data.get("message") or ["request failed"]))
        out = []
        for series in data["Results"]["series"]:
            sid = series["seriesID"]
            for obs in series["data"][:limit]:
                out.append(
                    self.record(
                        id=f"{sid}:{obs['year']}{obs['period']}",
                        title=f"BLS series {sid}",
                        retrieved_at=retrieved,
                        url=f"https://data.bls.gov/timeseries/{sid}",
                        series_id=sid,
                        value=float(obs["value"].replace(",", "")) if obs["value"] not in ("-", "") else None,
                        period=f"{obs['year']} {obs['periodName']}",
                        data={"latest": obs.get("latest") == "true"},
                    )
                )
        return out
