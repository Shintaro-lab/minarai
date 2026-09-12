from pathlib import Path

from minarai.artifacts.loader import load_artifact
from minarai.artifacts.renderer import render_artifact_html


def test_rendered_html_contains_artifact_title(valid_artifact_path: Path) -> None:
    artifact = load_artifact(valid_artifact_path)
    html = render_artifact_html(artifact)

    assert artifact.title in html


def test_rendered_html_preserves_section_ids(valid_artifact_path: Path) -> None:
    artifact = load_artifact(valid_artifact_path)
    html = render_artifact_html(artifact)

    for section_id in artifact.section_ids():
        assert f'data-section-id="{section_id}"' in html


def test_markdown_paragraphs_become_html(valid_artifact_path: Path) -> None:
    artifact = load_artifact(valid_artifact_path)
    html = render_artifact_html(artifact)

    assert "<p>" in html
