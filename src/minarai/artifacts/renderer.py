"""Render a validated Artifact to an HTML Viewer page.

HTML produced here is a disposable view: it can always be regenerated from
the Artifact YAML, and nothing in this module reads state back out of it.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional, Union

import markdown as _markdown
import nh3
from jinja2 import Environment, FileSystemLoader, select_autoescape

from minarai.artifacts.models import Artifact
from minarai.paths import viewer_dir as default_viewer_dir

_MARKDOWN_EXTENSIONS = ["fenced_code", "tables"]


def _render_markdown(text: str) -> str:
    """Markdown -> sanitized HTML.

    Section content is authored by whoever wrote the Artifact (which may be
    an AI agent or another contributor, not the person viewing it), so raw
    HTML passed through by python-markdown must be sanitized before it is
    marked `safe` in the template - otherwise a <script> in an Artifact
    would run in the reviewer's browser (stored XSS).
    """
    raw_html = _markdown.markdown(text, extensions=_MARKDOWN_EXTENSIONS)
    return nh3.clean(raw_html)


def render_artifact_html(artifact: Artifact, viewer_dir: Optional[Union[str, Path]] = None) -> str:
    templates_dir = Path(viewer_dir or default_viewer_dir()) / "templates"
    env = Environment(
        loader=FileSystemLoader(str(templates_dir)),
        autoescape=select_autoescape(["html"]),
    )
    template = env.get_template("artifact.html.jinja")

    sections = [
        {
            "id": section.id,
            "title": section.title,
            "html": _render_markdown(section.content),
        }
        for section in artifact.sections
    ]

    return template.render(artifact=artifact, sections=sections)
