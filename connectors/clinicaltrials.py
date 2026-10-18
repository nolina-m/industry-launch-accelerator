"""ClinicalTrials.gov API v2: research activity by condition, intervention or sponsor (no key)."""

from connectors.base import Connector


class ClinicalTrials(Connector):
    id = "clinicaltrials"
    name = "ClinicalTrials.gov"
    base_url = "https://clinicaltrials.gov/api/v2"

    def _search(self, query, status=None, limit=20):
        params = {
            "query.term": query,
            "pageSize": limit,
            "countTotal": "true",
            "fields": "NCTId,BriefTitle,OverallStatus,StartDate,LeadSponsorName",
        }
        if status:
            params["filter.overallStatus"] = status
        data, retrieved = self.request(f"{self.base_url}/studies", params)
        out = []
        if "totalCount" in data:
            out.append(
                self.record(
                    id=f"count:{query}",
                    title=f"Studies matching '{query}'",
                    url="https://clinicaltrials.gov/",
                    retrieved_at=retrieved,
                    series_id=f"studies?query.term={query}",
                    value=data["totalCount"],
                    unit="studies",
                )
            )
        for s in data.get("studies", []):
            p = s["protocolSection"]
            nct = p["identificationModule"]["nctId"]
            out.append(
                self.record(
                    id=nct,
                    title=p["identificationModule"].get("briefTitle", ""),
                    retrieved_at=retrieved,
                    url=f"https://clinicaltrials.gov/study/{nct}",
                    published_at=p.get("statusModule", {}).get("startDateStruct", {}).get("date"),
                    data={
                        "status": p.get("statusModule", {}).get("overallStatus"),
                        "sponsor": p.get("sponsorCollaboratorsModule", {}).get("leadSponsor", {}).get("name"),
                    },
                )
            )
        return out
