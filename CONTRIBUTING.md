# Contributing

Thanks for your interest. Full contribution guidelines (issues, pull requests, adding industry packs and data sources) are coming before the first release.

## Running the tests

```bash
./setup.sh --dev
.venv/bin/python -m ruff check .
.venv/bin/python -m pytest
```

Tests never use the network. Please do not add example launches, sample companies or sample outputs to the repo; tests use small inline data only.
