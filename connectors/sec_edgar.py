"""SEC EDGAR: company filings, full-text search and reported financials (no key; contact email required)."""

from connectors.base import Connector


class SecEdgar(Connector):
    id = "sec-edgar"
    name = "SEC EDGAR"
    base_url = "https://data.sec.gov"
    min_interval = 0.15  # SEC allows up to 10 requests per second
    needs_contact = True

    def _search(self, query, forms="10-K,10-Q,8-K", start=None, end=None, limit=20):
        """Full-text search of filings since 2001, e.g. search('"prior authorization"', forms="10-K")."""
        params = {"q": query, "forms": forms}
        if start and end:
            params.update({"dateRange": "custom", "startdt": start, "enddt": end})
        data, retrieved = self.request("https://efts.sec.gov/LATEST/search-index", params)
        out = []
        for hit in data["hits"]["hits"][:limit]:
            s = hit["_source"]
            accession = s["adsh"]
            cik = (s.get("ciks") or [""])[0].lstrip("0")
            doc = hit["_id"].split(":", 1)[-1]
            url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession.replace('-', '')}/{doc}"
            out.append(
                self.record(
                    id=hit["_id"],
                    title=f"{(s.get('display_names') or ['?'])[0]}: {s.get('form')} ({s.get('file_type')})",
                    url=url,
                    retrieved_at=retrieved,
                    published_at=s.get("file_date"),
                    series_id=f"EDGAR:{accession}",
                    data={"form": s.get("form"), "period_ending": s.get("period_ending"), "cik": cik},
                )
            )
        return out

    def _fetch(self, cik, concept=None, taxonomy="us-gaap", limit=10):
        """fetch(cik) lists recent filings; fetch(cik, concept="Revenues") returns reported values."""
        cik10 = str(cik).zfill(10)
        if concept:
            data, retrieved = self.request(
                f"{self.base_url}/api/xbrl/companyconcept/CIK{cik10}/{taxonomy}/{concept}.json"
            )
            out = []
            for unit, facts in data.get("units", {}).items():
                annual = [f for f in facts if f.get("form") == "10-K" and f.get("fp") == "FY"]
                for f in sorted(annual, key=lambda x: x["end"], reverse=True)[:limit]:
                    out.append(
                        self.record(
                            id=f"{cik10}:{concept}:{f['end']}",
                            title=f"{data['entityName']}: {data.get('label') or concept}",
                            url=f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik10}",
                            retrieved_at=retrieved,
                            published_at=f.get("filed"),
                            series_id=f"{taxonomy}:{concept}",
                            value=f["val"],
                            unit=unit,
                            period=f"{f.get('start', '')}..{f['end']}",
                            data={"accession": f.get("accn"), "form": f.get("form"), "fy": f.get("fy")},
                        )
                    )
            return out
        data, retrieved = self.request(f"{self.base_url}/submissions/CIK{cik10}.json")
        recent = data["filings"]["recent"]
        out = []
        for i in range(min(limit, len(recent["accessionNumber"]))):
            acc = recent["accessionNumber"][i]
            doc = recent.get("primaryDocument", [""] * (i + 1))[i]
            out.append(
                self.record(
                    id=acc,
                    title=f"{data['name']}: {recent['form'][i]}",
                    url=f"https://www.sec.gov/Archives/edgar/data/{int(cik10)}/{acc.replace('-', '')}/{doc}",
                    retrieved_at=retrieved,
                    published_at=recent["filingDate"][i],
                    series_id=f"EDGAR:{acc}",
                    data={"form": recent["form"][i], "sic": data.get("sicDescription")},
                )
            )
        return out
