"""EUR-Lex via the EU Publications Office SPARQL endpoint: EU legislation (no registration needed)."""

from connectors.base import Connector

QUERY = """PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
SELECT DISTINCT ?work ?celex ?title ?date WHERE {{
  ?work cdm:resource_legal_id_celex ?celex ; cdm:work_date_document ?date .
  ?expr cdm:expression_belongs_to_work ?work ; cdm:expression_title ?title ;
        cdm:expression_uses_language <http://publications.europa.eu/resource/authority/language/ENG> .
  FILTER(CONTAINS(LCASE(STR(?title)), "{term}"))
  FILTER(?date >= "{since}"^^<http://www.w3.org/2001/XMLSchema#date>){extra}
}} ORDER BY DESC(?date) LIMIT {limit}"""


class EurLex(Connector):
    id = "eurlex"
    name = "EUR-Lex"
    base_url = "https://publications.europa.eu/webapi/rdf/sparql"
    min_interval = 1.0

    def headers(self):
        return {**super().headers(), "Accept": "application/sparql-results+json"}

    def _search(self, query, since="2020-01-01", legal_acts_only=True, limit=20):
        """legal_acts_only keeps CELEX sector 3 (regulations, directives, decisions)."""
        term = query.lower().replace('"', "").replace("\\", "")
        extra = '\n  FILTER(STRSTARTS(STR(?celex), "3"))' if legal_acts_only else ""
        sparql = QUERY.format(term=term, since=since, limit=limit, extra=extra)
        data, retrieved = self.request(self.base_url, {"query": sparql, "format": "application/sparql-results+json"})
        out = []
        for b in data["results"]["bindings"]:
            celex = b["celex"]["value"]
            out.append(
                self.record(
                    id=celex,
                    title=b["title"]["value"],
                    retrieved_at=retrieved,
                    url=f"https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:{celex}",
                    published_at=b["date"]["value"],
                    series_id=f"CELEX:{celex}",
                    data={"work": b["work"]["value"]},
                )
            )
        return out
