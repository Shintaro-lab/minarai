"""Load Artifact YAML files into validated Artifact objects."""
from __future__ import annotations

from pathlib import Path
from typing import Optional, Union

import yaml

from minarai.artifacts.models import Artifact
from minarai.artifacts.validator import validate_artifact_data


def load_artifact_data(path: Union[str, Path]) -> dict:
    """Read the raw YAML data without validating it."""
    with Path(path).open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_artifact(path: Union[str, Path], schema_path: Optional[Union[str, Path]] = None) -> Artifact:
    """Read, validate and parse an Artifact YAML file.

    Raises ArtifactValidationError if the data does not conform to
    artifacts/schema/artifact.schema.json.
    """
    data = load_artifact_data(path)
    validate_artifact_data(data, schema_path=schema_path)
    return Artifact.from_dict(data)
