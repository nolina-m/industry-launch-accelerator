"""Text extraction from input files (FR-INT-01, FR-INP-02)."""

from scripts.extract.extract import extract_launch, extract_text
from scripts.util import load_yaml
from tests.docbuilders import make_docx, make_pdf, make_pptx


def test_markdown_and_text(tmp_path):
    (tmp_path / "a.md").write_text("# Title\nbody")
    (tmp_path / "b.txt").write_text("plain")
    assert extract_text(tmp_path / "a.md").text == "# Title\nbody"
    assert extract_text(tmp_path / "b.txt").text == "plain"


def test_docx_keeps_headings_and_tables(tmp_path):
    path = make_docx(tmp_path / "x.docx", "Overview", "Placeholder paragraph.", [["col1", "col2"], ["a", "b"]])
    result = extract_text(path)
    assert result.status == "ok"
    assert "# Overview" in result.text
    assert "Placeholder paragraph." in result.text
    assert "| a | b |" in result.text


def test_pptx_includes_speaker_notes(tmp_path):
    path = make_pptx(tmp_path / "x.pptx", "Slide title", notes="Talk track here")
    result = extract_text(path)
    assert "Slide title" in result.text
    assert "[speaker notes] Talk track here" in result.text


def test_pdf_text(tmp_path):
    path = make_pdf(tmp_path / "x.pdf", "Placeholder text for a PDF page that is long enough to count as real text")
    result = extract_text(path)
    assert result.status == "ok"
    assert "Placeholder text" in result.text


def test_pdf_with_almost_no_text_is_flagged_as_possibly_scanned(tmp_path):
    result = extract_text(make_pdf(tmp_path / "scan.pdf", "x"))
    assert result.status == "warning"
    assert "scanned" in result.note


def test_unsupported_and_broken_files_never_crash(tmp_path):
    (tmp_path / "logo.png").write_bytes(b"\x89PNG")
    (tmp_path / "broken.docx").write_bytes(b"not a real docx")
    assert extract_text(tmp_path / "logo.png").status == "skipped"
    broken = extract_text(tmp_path / "broken.docx")
    assert broken.status == "error" and "could not be read" in broken.note


def test_extract_launch_writes_text_outside_inputs(tmp_path):
    (tmp_path / "inputs" / "brief").mkdir(parents=True)
    (tmp_path / "inputs" / "brief" / "notes.md").write_text("hello")
    (tmp_path / "inputs" / ".DS_Store").write_text("")
    results = extract_launch(tmp_path)
    assert [r.path.name for r in results] == ["notes.md"]
    assert (tmp_path / "intake" / "extracted" / "inputs__brief__notes.md.txt").read_text() == "hello"
    manifest = load_yaml(tmp_path / "intake" / "manifest.yaml")
    assert manifest["files"][0]["file"] == "inputs/brief/notes.md"
    assert not any(p.name.endswith(".txt") for p in (tmp_path / "inputs").rglob("*"))
