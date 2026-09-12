"""In-memory representation of a validated Artifact.

Deliberately a single, generic shape (one dataclass, no per-type subclasses)
regardless of ``type`` (design/test/standard/...); see docs/concepts.md.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ArtifactSection:
    id: str
    title: str
    content: str


@dataclass
class Artifact:
    id: str
    type: str
    title: str
    status: str
    sections: list[ArtifactSection] = field(default_factory=list)

    def section_ids(self) -> list[str]:
        return [section.id for section in self.sections]

    def get_section(self, section_id: str) -> Optional[ArtifactSection]:
        for section in self.sections:
            if section.id == section_id:
                return section
        return None

    @classmethod
    def from_dict(cls, data: dict) -> "Artifact":
        sections = [
            ArtifactSection(id=s["id"], title=s["title"], content=s.get("content", ""))
            for s in data.get("sections", [])
        ]
        return cls(
            id=data["id"],
            type=data["type"],
            title=data["title"],
            status=data["status"],
            sections=sections,
        )
