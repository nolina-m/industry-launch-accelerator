"""World Bank Indicators API: country-level economic data (no key)."""

from connectors.base import Connector


class WorldBank(Connector):
    id = "worldbank"
    name = "World Bank"
    base_url = "https://api.worldbank.org/v2"

    def _fetch(self, indicator, country="US", limit=10):
        """fetch("NY.GDP.MKTP.CD", country="US;DE")."""
        data, retrieved = self.request(
            f"{self.base_url}/country/{country}/indicator/{indicator}",
            {"format": "json", "per_page": limit, "mrv": limit},
        )
        if not isinstance(data, list) or len(data) < 2 or data[1] is None:
            return []
        return [
            self.record(
                id=f"{o['countryiso3code']}:{indicator}:{o['date']}",
                title=f"{o['indicator']['value']}: {o['country']['value']}",
                url=f"https://data.worldbank.org/indicator/{indicator}?locations={o['country']['id']}",
                retrieved_at=retrieved,
                series_id=indicator,
                value=o.get("value"),
                period=o.get("date"),
                unit=o.get("unit") or None,
            )
            for o in data[1]
            if o.get("value") is not None
        ]
