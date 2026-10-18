"""Arbeitnow: a free job-board API, mostly European jobs (no key). Hiring signals."""

from datetime import datetime, timezone

from connectors.base import Connector


class Arbeitnow(Connector):
    id = "arbeitnow"
    name = "Arbeitnow"
    base_url = "https://www.arbeitnow.com/api/job-board-api"
    min_interval = 1.0

    def _search(self, query, pages=1, limit=25):
        """The API has no search: it lists recent jobs, filtered here by the query words."""
        words = [w.lower() for w in query.split()]
        out = []
        for page in range(1, pages + 1):
            data, retrieved = self.request(self.base_url, {"page": page})
            for job in data["data"]:
                text = " ".join([job["title"], job["company_name"], " ".join(job.get("tags", []))]).lower()
                if all(w in text for w in words):
                    posted = datetime.fromtimestamp(job["created_at"], tz=timezone.utc).date().isoformat()
                    out.append(
                        self.record(
                            id=job["slug"],
                            title=f"{job['company_name']}: {job['title']}",
                            url=job["url"],
                            retrieved_at=retrieved,
                            published_at=posted,
                            data={
                                "company": job["company_name"],
                                "location": job.get("location"),
                                "remote": job.get("remote"),
                                "tags": job.get("tags", []),
                            },
                        )
                    )
        return out[:limit]
