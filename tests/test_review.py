from pathlib import Path

import pytest

from minarai.artifacts.loader import load_artifact
from minarai.review import store
from minarai.review.store import (
    CommentNotFoundError,
    InvalidArtifactIdError,
    SectionNotFoundError,
)


def test_add_comment_to_existing_section(valid_artifact_path: Path, reviews_dir: Path) -> None:
    artifact = load_artifact(valid_artifact_path)

    comment = store.add_comment(
        artifact, "authentication", "Refresh Tokenについても記載してください。", reviews_dir
    )

    assert comment.id == "review-001"
    assert comment.target == "authentication"
    assert comment.status == "open"


def test_add_comment_to_missing_section_raises(valid_artifact_path: Path, reviews_dir: Path) -> None:
    artifact = load_artifact(valid_artifact_path)

    with pytest.raises(SectionNotFoundError):
        store.add_comment(artifact, "does-not-exist", "comment", reviews_dir)


def test_comment_is_persisted_to_review_yaml(valid_artifact_path: Path, reviews_dir: Path) -> None:
    artifact = load_artifact(valid_artifact_path)
    store.add_comment(artifact, "authentication", "指摘です。", reviews_dir)

    review_file = reviews_dir / f"{artifact.id}.yaml"
    assert review_file.exists()
    assert "指摘です。" in review_file.read_text(encoding="utf-8")


def test_update_comment_status(valid_artifact_path: Path, reviews_dir: Path) -> None:
    artifact = load_artifact(valid_artifact_path)
    comment = store.add_comment(artifact, "authentication", "指摘です。", reviews_dir)

    updated = store.update_comment_status(comment.id, "addressed", reviews_dir)

    assert updated.status == "addressed"
    reloaded = store.list_comments(artifact.id, reviews_dir)
    assert reloaded[0].status == "addressed"


def test_update_unknown_comment_raises(reviews_dir: Path) -> None:
    with pytest.raises(CommentNotFoundError):
        store.update_comment_status("review-999", "resolved", reviews_dir)


def test_list_comments_returns_all_for_artifact(valid_artifact_path: Path, reviews_dir: Path) -> None:
    artifact = load_artifact(valid_artifact_path)
    store.add_comment(artifact, "overview", "comment 1", reviews_dir)
    store.add_comment(artifact, "authentication", "comment 2", reviews_dir)

    comments = store.list_comments(artifact.id, reviews_dir)

    assert [c.id for c in comments] == ["review-001", "review-002"]
    assert [c.target for c in comments] == ["overview", "authentication"]


def test_list_comments_for_unreviewed_artifact_is_empty(reviews_dir: Path) -> None:
    assert store.list_comments("no-such-artifact", reviews_dir) == []


def test_review_path_rejects_path_traversal_artifact_id(reviews_dir: Path) -> None:
    with pytest.raises(InvalidArtifactIdError):
        store.review_path("../../etc/passwd", reviews_dir)


def test_review_path_rejects_path_separators_in_artifact_id(reviews_dir: Path) -> None:
    with pytest.raises(InvalidArtifactIdError):
        store.review_path("some/nested/path", reviews_dir)
