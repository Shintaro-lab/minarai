"""Path resolution for Minarai's resources.

Centralized here so the rest of the package never hardcodes where
``artifacts/``, the review viewer, or ``reviews/`` live. Each path can be
overridden with an environment variable, which keeps the door open for
per-project locations later without changing calling code.
"""
from __future__ import annotations

import os
from pathlib import Path


def _repo_root() -> Path:
    # This file lives at <repo_root>/src/minarai/paths.py
    return Path(__file__).resolve().parents[2]


def schema_path() -> Path:
    override = os.environ.get("MINARAI_ARTIFACT_SCHEMA")
    if override:
        return Path(override)
    return _repo_root() / "artifacts" / "schema" / "artifact.schema.json"


def viewer_dir() -> Path:
    override = os.environ.get("MINARAI_VIEWER_DIR")
    if override:
        return Path(override)
    # Viewer templates/static ship inside the review package itself, not as
    # a top-level repository resource like artifacts/ or reviews/.
    return Path(__file__).resolve().parent / "review" / "viewer"


def reviews_dir() -> Path:
    override = os.environ.get("MINARAI_REVIEWS_DIR")
    if override:
        return Path(override)
    return _repo_root() / "reviews"
