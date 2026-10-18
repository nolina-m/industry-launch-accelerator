"""U.S. Census Bureau Data API: business counts, employment, demographics (free key required since May 2026)."""

from connectors.base import Connector


class Census(Connector):
    id = "census"
    name = "U.S. Census Bureau"
    base_url = "https://api.census.gov/data"
    key_env = "CENSUS_API_KEY"
    key_required = True

    def auth_params(self):
        return {"key": self.key} if self.key else {}

    def _fetch(self, dataset, get, geography="us:*", **predicates):
        """fetch("2022/cbp", get="ESTAB,EMP,NAICS2017_LABEL", NAICS2017="622")."""
        params = {"get": get, "for": geography, **predicates}
        data, retrieved = self.request(f"{self.base_url}/{dataset}", params)
        header, rows = data[0], data[1:]
        series = f"{dataset}?" + "&".join(f"{k}={v}" for k, v in sorted(params.items()))
        out = []
        for row in rows:
            item = dict(zip(header, row, strict=False))
            label = " / ".join(str(v) for k, v in item.items() if k.endswith("_LABEL") or k == "NAME")
            for var in get.split(","):
                if var.endswith("_LABEL") or var == "NAME":
                    continue
                out.append(
                    self.record(
                        id=f"{dataset}:{var}:{row[-1]}",
                        title=f"{var} {label}".strip(),
                        url=f"{self.base_url}/{dataset}",
                        retrieved_at=retrieved,
                        series_id=f"{series}#{var}",
                        value=_num(item.get(var)),
                        data=item,
                    )
                )
        return out


def _num(v):
    try:
        return float(v) if "." in str(v) else int(v)
    except (TypeError, ValueError):
        return v
