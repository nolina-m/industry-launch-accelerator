# Contributing

Thanks for helping make Industry Launch Accelerator better. You don't need to write code to contribute: feedback from product marketers who've used it is the most useful thing of all.

## Issues

[Open an issue](https://github.com/nolina-m/industry-launch-accelerator/issues/new/choose) and pick a form:

- **Bug:** something broke or behaved unexpectedly. Include what you asked the agent, which agent and version, and what happened.
- **Feedback:** how usable the kit was as a starting point (1–5), and what would make it better.
- **New industry pack:** propose a pack for an industry that doesn't have one.
- **New data source:** suggest a public data source. It must be free to use for business purposes.

**Please never paste confidential material** into an issue: product briefs, customer names, internal documents or access keys.

## Pull requests

1. Fork the repo and create a branch.
2. Set up with the test tools:
   ```bash
   ./setup.sh --dev
   ```
3. Make your change, then run the checks. Both must pass; they also run automatically on every pull request.
   ```bash
   .venv/bin/python -m ruff check .
   .venv/bin/python -m pytest
   ```
4. If your change affects a requirement, update `docs/requirements-trace.md`.
5. Open the pull request, saying what changed and why.

Guides for common changes:
- [Add or improve an industry pack](docs/customization.md#add-or-improve-an-industry-pack)
- [Add a data source](docs/adding-a-data-source.md)
- Change what the agent does at a stage: edit the matching file in `instructions/`. Keep it plain Markdown that any coding agent can follow (no tool-specific commands).

## Ground rules for the repo

- **No example launches, sample companies or sample outputs.** Tests use small inline placeholder data ("Placeholder Co", "Competitor A"). Connector tests use recorded responses in the real API shape, with placeholder values.
- **Public information only.** Nothing non-public about any company, and no real company's logos or brand materials.
- **No vendors in industry packs.** Packs list regulators, associations and public sources; competitors belong in each launch's research.
- **Data sources must allow business use** on their free tier, and must be reached through an official API. No scraping, logins or paywall workarounds.
- **Tests never touch the network.** `tests/conftest.py` blocks it.
- **Keep it agent-neutral.** Instructions must work for any agent that can read files and run shell commands.

## License

By contributing, you agree that your contributions are licensed under the [MIT License](LICENSE).
