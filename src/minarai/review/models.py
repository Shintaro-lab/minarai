"""Review Feedback data models.

``ReviewComment`` is kept independent of any LLM or Experience code so that,
later, a sequence of (Artifact before, human comment, Artifact after, review
result) can be turned into an Experience without this module changing.
"""
from __future__ import annotations

from dataclasses import dataclass, field

VALID_STATUSES: tuple[str, ...] = ("open", "addressed", "resolved")


@dataclass
class ReviewComment:
    id: str
    target: str
    comment: str
    status: str = "open"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "target": self.target,
            "comment": self.comment,
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ReviewComment":
        return cls(
            id=data["id"],
            target=data["target"],
            comment=data["comment"],
            status=data.get("status", "open"),
        )


@dataclass
class ArtifactReview:
    artifact_id: str
    comments: list[ReviewComment] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "artifact_id": self.artifact_id,
            "comments": [comment.to_dict() for comment in self.comments],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ArtifactReview":
        comments = [ReviewComment.from_dict(c) for c in data.get("comments", [])]
        return cls(artifact_id=data["artifact_id"], comments=comments)
