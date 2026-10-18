"""Data USA (Tesseract API): ready-made US statistics from Census, BLS and others (no key)."""

from connectors.base import Connector


class DataUsa(Connector):
    id = "datausa"
    name = "Data USA"
    base_url = "https://api.datausa.io/tesseract/data.jsonrecords"

    def _fetch(self, cube, measures, drilldowns="Year,Nation", **cuts):
        """fetch("acs_yg_total_population_1", measures="Population")."""
        params = {"cube": cube, "measures": measures, "drilldowns": drilldowns, **cuts}
        data, retrieved = self.request(self.base_url, params)
        meta = data.get("annotations", {})
        out = []
        for row in data["data"]:
            for m in measures.split(","):
                label = " / ".join(str(row[d]) for d in drilldowns.split(",") if d in row)
                out.append(
                    self.record(
                        id=f"{cube}:{m}:{label}",
                        title=f"{m} ({label})",
                        retrieved_at=retrieved,
                        url="https://datausa.io/",
                        series_id=f"{cube}#{m}",
                        value=row.get(m),
                        period=str(row.get("Year", "")) or None,
                        data={
                            "source": meta.get("source_name"),
                            "dataset": meta.get("dataset_name"),
                            "table_id": meta.get("table_id"),
                        },
                    )
                )
        return out
