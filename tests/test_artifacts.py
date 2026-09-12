from pathlib import Path

import pytest

from minarai.artifacts.loader import load_artifact, load_artifact_data
from minarai.artifacts.renderer import render_artifact_html
from minarai.artifacts.validator import ArtifactValidationError, validate_artifact_data


def test_load_valid_artifact(valid_artifact_path: Path) -> None:
    artifact = load_artifact(valid_artifact_path)

    assert artifact.id == "sample-auth-design"
    assert artifact.type == "design"
    assert artifact.status == "draft"
    assert artifact.section_ids() == ["overview", "authentication"]


def test_missing_required_field_raises_validation_error(tmp_path: Path) -> None:
    path = tmp_path / "invalid.yaml"
    path.write_text(
        "id: broken\ntype: design\nstatus: draft\nsections: []\n",
        encoding="utf-8",
    )

    with pytest.raises(ArtifactValidationError) as exc_info:
        load_artifact(path)

    assert any("title" in error for error in exc_info.value.errors)


def test_path_traversal_artifact_id_raises_validation_error() -> None:
    data = {
        "id": "../../etc/passwd",
        "type": "design",
        "title": "Malicious",
        "status": "draft",
        "sections": [{"id": "a", "title": "A", "content": "x"}],
    }

    with pytest.raises(ArtifactValidationError):
        validate_artifact_data(data)


def test_path_traversal_section_id_raises_validation_error() -> None:
    data = {
        "id": "safe-id",
        "type": "design",
        "title": "Malicious",
        "status": "draft",
        "sections": [{"id": "../escape", "title": "A", "content": "x"}],
    }

    with pytest.raises(ArtifactValidationError):
        validate_artifact_data(data)


def test_duplicate_section_id_raises_validation_error() -> None:
    data = {
        "id": "dup",
        "type": "design",
        "title": "Dup",
        "status": "draft",
        "sections": [
            {"id": "a", "title": "A", "content": "x"},
            {"id": "a", "title": "A again", "content": "y"},
        ],
    }

    with pytest.raises(ArtifactValidationError) as exc_info:
        validate_artifact_data(data)

    assert any("duplicate section id" in error for error in exc_info.value.errors)


def test_markdown_content_is_rendered_to_html(valid_artifact_path: Path) -> None:
    artifact = load_artifact(valid_artifact_path)
    html = render_artifact_html(artifact)

    assert "<strong>Authorization Code Flow + PKCE</strong>" in html


def test_raw_html_in_markdown_content_is_sanitized(tmp_path: Path) -> None:
    path = tmp_path / "xss.yaml"
    path.write_text(
        "id: xss-artifact\n"
        "type: design\n"
        "title: XSS\n"
        "status: draft\n"
        "sections:\n"
        "  - id: overview\n"
        "    title: Overview\n"
        "    content: |\n"
        "      <script>alert('xss')</script>\n"
        "      <img src=x onerror=\"alert('xss')\">\n",
        encoding="utf-8",
    )

    artifact = load_artifact(path)
    html = render_artifact_html(artifact)

    # The page's own <script src="/static/app.js"> tag is expected; only the
    # Artifact-supplied payload must be stripped.
    assert "<script>alert" not in html
    assert "onerror" not in html


def test_load_artifact_data_returns_raw_dict(valid_artifact_path: Path) -> None:
    data = load_artifact_data(valid_artifact_path)

    assert data["id"] == "sample-auth-design"
    assert isinstance(data["sections"], list)
