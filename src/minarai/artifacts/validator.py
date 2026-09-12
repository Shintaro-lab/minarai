"""Schema validation for Artifact YAML data.

Validates structure via JSON Schema (artifacts/schema/artifact.schema.json)
and additionally rejects duplicate Section ids within one Artifact, which
plain JSON Schema cannot express.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional, Union

import jsonschema

from minarai.paths import schema_path as default_schema_path


class ArtifactValidationError(Exception):
    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__("; ".join(errors))


def _load_schema(schema_path: Optional[Union[str, Path]] = None) -> dict:
    path = Path(schema_path) if schema_path else default_schema_path()
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def validate_artifact_data(data: dict, schema_path: Optional[Union[str, Path]] = None) -> None:
    """Raise ArtifactValidationError if `data` is not a valid Artifact."""
    schema = _load_schema(schema_path)
    validator_cls = jsonschema.validators.validator_for(schema)
    validator_cls.check_schema(schema)
    validator = validator_cls(schema)

    errors = [
        f"{'/'.join(str(p) for p in err.path) or '<root>'}: {err.message}"
        for err in sorted(validator.iter_errors(data), key=str)
    ]

    seen_ids: set[str] = set()
    duplicate_ids: set[str] = set()
    sections = data.get("sections", []) if isinstance(data, dict) else []
    for section in sections:
        section_id = section.get("id") if isinstance(section, dict) else None
        if section_id is None:
            continue
        if section_id in seen_ids:
            duplicate_ids.add(section_id)
        seen_ids.add(section_id)

    for duplicate_id in sorted(duplicate_ids):
        errors.append(f"sections: duplicate section id '{duplicate_id}'")

    if errors:
        raise ArtifactValidationError(errors)
