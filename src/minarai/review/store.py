"""Persistence for Review Feedback (Review YAML files, one per Artifact).

Artifact YAML stays the Source of Truth; this module never writes into it.
Review YAML holds human feedback only, keyed by Artifact section id.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Optional, Union

import yaml

from minarai.artifacts.models import Artifact
from minarai.paths import reviews_dir as default_reviews_dir
from minarai.review.models import ArtifactReview, ReviewComment, VALID_STATUSES

_COMMENT_ID_RE = re.compile(r"review-(\d+)$")
_SAFE_ARTIFACT_ID_RE = re.compile(r"^[A-Za-z0-9_-]+$")


class ReviewError(Exception):
    pass


class SectionNotFoundError(ReviewError):
    pass


class CommentNotFoundError(ReviewError):
    pass


class InvalidArtifactIdError(ReviewError):
    pass


def _resolve_reviews_dir(reviews_dir: Optional[Union[str, Path]]) -> Path:
    directory = Path(reviews_dir) if reviews_dir else default_reviews_dir()
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def review_path(artifact_id: str, reviews_dir: Optional[Union[str, Path]] = None) -> Path:
    # artifact_id names the Review YAML file directly; the Artifact schema
    # already restricts it to this pattern, but that guarantee lives in a
    # separate file (and can be pointed elsewhere via schema_path), so it is
    # re-checked here to stop path traversal (e.g. id: "../../etc/passwd")
    # even if schema validation was skipped or overridden upstream.
    if not _SAFE_ARTIFACT_ID_RE.match(artifact_id):
        raise InvalidArtifactIdError(
            f"Invalid artifact id '{artifact_id}': only letters, digits, '_' and '-' are allowed"
        )
    return _resolve_reviews_dir(reviews_dir) / f"{artifact_id}.yaml"


def load_review(artifact_id: str, reviews_dir: Optional[Union[str, Path]] = None) -> ArtifactReview:
    path = review_path(artifact_id, reviews_dir)
    if not path.exists():
        return ArtifactReview(artifact_id=artifact_id)
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return ArtifactReview.from_dict(data)


def save_review(review: ArtifactReview, reviews_dir: Optional[Union[str, Path]] = None) -> Path:
    path = review_path(review.artifact_id, reviews_dir)
    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(review.to_dict(), f, allow_unicode=True, sort_keys=False)
    return path


def _next_comment_id(review: ArtifactReview) -> str:
    max_n = 0
    for comment in review.comments:
        match = _COMMENT_ID_RE.match(comment.id)
        if match:
            max_n = max(max_n, int(match.group(1)))
    return f"review-{max_n + 1:03d}"


def add_comment(
    artifact: Artifact,
    target: str,
    comment_text: str,
    reviews_dir: Optional[Union[str, Path]] = None,
) -> ReviewComment:
    if target not in artifact.section_ids():
        raise SectionNotFoundError(
            f"Section '{target}' does not exist in artifact '{artifact.id}'"
        )

    review = load_review(artifact.id, reviews_dir)
    comment = ReviewComment(
        id=_next_comment_id(review), target=target, comment=comment_text, status="open"
    )
    review.comments.append(comment)
    save_review(review, reviews_dir)
    return comment


def list_comments(artifact_id: str, reviews_dir: Optional[Union[str, Path]] = None) -> list[ReviewComment]:
    return load_review(artifact_id, reviews_dir).comments


def find_comment(
    comment_id: str, reviews_dir: Optional[Union[str, Path]] = None
) -> tuple[ArtifactReview, ReviewComment]:
    """Locate a comment by id across all Review YAML files.

    Comment ids are only unique within one Artifact's review file, but the
    `minarai review update <id>` CLI does not require the caller to name the
    Artifact, so all review files are scanned.
    """
    directory = _resolve_reviews_dir(reviews_dir)
    for path in sorted(directory.glob("*.yaml")):
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        if not data:
            continue
        review = ArtifactReview.from_dict(data)
        for comment in review.comments:
            if comment.id == comment_id:
                return review, comment
    raise CommentNotFoundError(f"Comment '{comment_id}' was not found in any review")


def update_comment_status(
    comment_id: str, status: str, reviews_dir: Optional[Union[str, Path]] = None
) -> ReviewComment:
    if status not in VALID_STATUSES:
        raise ReviewError(f"Invalid status '{status}', expected one of {VALID_STATUSES}")

    review, comment = find_comment(comment_id, reviews_dir)
    comment.status = status
    save_review(review, reviews_dir)
    return comment
