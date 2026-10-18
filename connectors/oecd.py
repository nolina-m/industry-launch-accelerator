"""OECD Data Explorer (SDMX API): cross-country statistics (no key)."""

from connectors.base import Connector


class Oecd(Connector):
    id = "oecd"
    name = "OECD"
    base_url = "https://sdmx.oecd.org/public/rest/data"
    min_interval = 1.5

    def _fetch(self, flow, key="all", start=None, limit=40):
        """fetch("OECD.SDD.NAD,DSD_NAMAIN1@DF_QNA,", key="Q..USA.S1..B1GQ._Z...USD_PPP.LR.LA.T0102", start="2024-Q1").

        Find flow and key codes on https://data-explorer.oecd.org ("Developer API" button).
        """
        params = {"dimensionAtObservation": "AllDimensions", "format": "jsondata"}
        if start:
            params["startPeriod"] = start
        data, retrieved = self.request(f"{self.base_url}/{flow}/{key}", params)
        dims = data["data"]["structure"]["dimensions"]["observation"]
        name = data["data"]["structure"].get("name", flow)
        out = []
        for coords, values in list(data["data"]["dataSets"][0]["observations"].items())[:limit]:
            parts = {d["id"]: d["values"][int(i)]["id"] for d, i in zip(dims, coords.split(":"), strict=False)}
            period = parts.pop("TIME_PERIOD", None)
            series = ".".join(parts.values())
            out.append(
                self.record(
                    id=f"{flow}/{series}/{period}",
                    title=name,
                    retrieved_at=retrieved,
                    url="https://data-explorer.oecd.org/",
                    series_id=f"{flow}/{series}",
                    value=values[0],
                    period=period,
                    data=parts,
                )
            )
        return out
