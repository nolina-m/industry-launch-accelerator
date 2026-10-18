"""GitHub: open-source momentum for competitors and technologies (no key; GITHUB_TOKEN raises limits)."""

from connectors.base import Connector


class GitHub(Connector):
    id = "github"
    name = "GitHub"
    base_url = "https://api.github.com"
    key_env = "GITHUB_TOKEN"
    min_interval = 1.0

    def headers(self):
        h = {**super().headers(), "Accept": "application/vnd.github+json"}
        if self.key:
            h["Authorization"] = f"Bearer {self.key}"
        return h

    def _repo(self, r, retrieved):
        return self.record(
            id=r["full_name"],
            title=r["full_name"],
            url=r["html_url"],
            retrieved_at=retrieved,
            published_at=(r.get("created_at") or "")[:10] or None,
            summary=r.get("description") or "",
            series_id="stargazers_count",
            value=r.get("stargazers_count"),
            unit="stars",
            data={
                "forks": r.get("forks_count"),
                "open_issues": r.get("open_issues_count"),
                "pushed_at": r.get("pushed_at"),
                "language": r.get("language"),
            },
        )

    def _search(self, query, sort="stars", limit=10):
        data, retrieved = self.request(
            f"{self.base_url}/search/repositories", {"q": query, "sort": sort, "per_page": limit}
        )
        return [self._repo(r, retrieved) for r in data["items"]]

    def _fetch(self, full_name):
        data, retrieved = self.request(f"{self.base_url}/repos/{full_name}")
        return [self._repo(data, retrieved)]
