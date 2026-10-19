"""Repository rules (read-first rules 3, 4 and 6; FR-GRD-04, FR-GRD-05, FR-TST-02, FR-DOC-*)."""

import re
import subprocess

import pytest

from scripts.util import REPO_ROOT


def tracked_files() -> list[str]:
    try:
        out = subprocess.run(["git", "ls-files"], cwd=REPO_ROOT, capture_output=True, text=True, check=True).stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        pytest.skip("not a git checkout")
    files = [f for f in out.splitlines() if f]
    if not files:
        pytest.skip("nothing tracked yet")
    return files


def test_no_private_build_documents_are_tracked():
    for f in tracked_files():
        name = f.rsplit("/", 1)[-1]
        assert not re.search(r"PRD", name), f
        assert name != "BUILD-NOTES.md", f
        assert name != ".env", f


def test_no_launches_or_sample_outputs_are_tracked():
    for f in tracked_files():
        assert not f.startswith("launches/") or f == "launches/.gitkeep", f
        assert "/outputs/" not in f and not f.startswith("outputs/"), f


def test_no_brand_assets_or_binary_samples_are_bundled():
    """FR-GRD-05: no real company's logos or brand materials; no binary sample documents."""
    allowed = {"docs/images/pipeline.svg"}
    for f in tracked_files():
        if f in allowed:
            continue
        assert not re.search(r"\.(png|jpe?g|gif|svg|pdf|docx|dotx|xlsx|pptx)$", f, re.I), f


def test_no_employer_or_job_application_mentions():
    phrases = re.compile(r"job application|applying for (?:a|the) (?:role|job|position)|hiring manager|recruiter|"
                         r"cover letter|take-home|interview loop", re.I)
    for f in tracked_files():
        path = REPO_ROOT / f
        if path.suffix in (".py", ".md", ".yaml", ".yml", ".json", ".j2", ".toml", ".txt", ".sh", ".ps1"):
            text = path.read_text(encoding="utf-8", errors="ignore")
            if f == "tests/test_repo_hygiene.py":
                continue
            assert not phrases.search(text), f


def test_docs_required_by_the_prd_exist():
    for f in ("README.md", "CONTRIBUTING.md", "LICENSE", "AGENTS.md", "CLAUDE.md", ".env.example",
              "docs/design-decisions.md", "docs/customization.md", "docs/data-sources.md",
              "docs/adding-a-data-source.md", "docs/compatibility.md", "docs/requirements-trace.md",
              "docs/images/pipeline.svg",
              ".github/ISSUE_TEMPLATE/bug_report.yml", ".github/ISSUE_TEMPLATE/feedback.yml",
              ".github/ISSUE_TEMPLATE/new_industry_pack.yml", ".github/ISSUE_TEMPLATE/new_data_source.yml"):
        assert (REPO_ROOT / f).is_file(), f


def test_readme_first_screen_and_sections():
    """FR-DOC-01..05: what it is, in/out, the diagram before any scrolling; then the required sections."""
    readme = (REPO_ROOT / "README.md").read_text()
    first_screen = readme.split("\n---\n")[0]
    assert "pipeline.svg" in first_screen and "What goes in" in first_screen and "What comes out" in first_screen
    for n in range(1, 9):
        assert f"| {n}. " in first_screen
    for heading in ("## How it works in 60 seconds", "## Quickstart", "## Example runs", "## About the author"):
        assert heading in readme
    assert "Example runs coming soon." in readme
    assert "https://nolina.work" in readme and "linkedin.com/in/" in readme


def test_design_decisions_has_owner_placeholder_and_topics():
    text = (REPO_ROOT / "docs" / "design-decisions.md").read_text()
    assert "placeholder" in text.split("\n## ")[0].lower()
    for topic in ("Cite or label", "Checkpoints", "Data first", "Pricing models, not prices", "Plain instructions",
                  "No slides"):
        assert topic in text, topic


def test_markdown_links_to_repo_files_resolve():
    docs = [f"docs/{p.name}" for p in (REPO_ROOT / "docs").glob("*.md")]
    for md in ("README.md", "CONTRIBUTING.md", "AGENTS.md", *docs):
        path = REPO_ROOT / md
        for target in re.findall(r"\]\((?!https?://|#|mailto:)([^)#\s]+)", path.read_text()):
            assert (path.parent / target).exists(), f"{md} links to missing {target}"


def test_feedback_form_has_the_1_to_5_rating():
    text = (REPO_ROOT / ".github" / "ISSUE_TEMPLATE" / "feedback.yml").read_text()
    assert "Usable as a starting point (1–5)" in text
    assert all(f'"{n}:' in text for n in range(1, 6))
