"""Local Review Server.

Serves the HTML Viewer (rendered fresh from the Artifact YAML on every
request) and a minimal JSON API for reading/writing Review Feedback. No
LLM or Experience code is imported here on purpose.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional, Union

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from minarai.artifacts.loader import load_artifact
from minarai.artifacts.models import Artifact
from minarai.artifacts.renderer import render_artifact_html
from minarai.artifacts.validator import ArtifactValidationError
from minarai.paths import viewer_dir as default_viewer_dir
from minarai.review import store


class CommentIn(BaseModel):
    target: str
    comment: str


def create_app(
    artifact_path: Union[str, Path],
    reviews_dir: Optional[Union[str, Path]] = None,
    viewer_dir: Optional[Union[str, Path]] = None,
) -> FastAPI:
    artifact_path = Path(artifact_path)
    viewer_root = Path(viewer_dir) if viewer_dir else default_viewer_dir()

    app = FastAPI(title="Minarai Artifact Review")
    app.mount("/static", StaticFiles(directory=str(viewer_root / "static")), name="static")

    def _load_artifact() -> Artifact:
        try:
            return load_artifact(artifact_path)
        except ArtifactValidationError as exc:
            raise HTTPException(status_code=500, detail="; ".join(exc.errors)) from exc

    @app.get("/", response_class=HTMLResponse)
    def viewer() -> str:
        artifact = _load_artifact()
        return render_artifact_html(artifact, viewer_dir=viewer_root)

    @app.get("/api/artifact")
    def get_artifact() -> dict:
        artifact = _load_artifact()
        return {
            "id": artifact.id,
            "type": artifact.type,
            "title": artifact.title,
            "status": artifact.status,
            "sections": [
                {"id": s.id, "title": s.title, "content": s.content} for s in artifact.sections
            ],
        }

    @app.get("/api/comments")
    def get_comments() -> list[dict]:
        artifact = _load_artifact()
        return [c.to_dict() for c in store.list_comments(artifact.id, reviews_dir)]

    @app.post("/api/comments", status_code=201)
    def post_comment(payload: CommentIn) -> dict:
        artifact = _load_artifact()
        try:
            comment = store.add_comment(artifact, payload.target, payload.comment, reviews_dir)
        except store.SectionNotFoundError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return comment.to_dict()

    return app


def run_server(
    artifact_path: Union[str, Path],
    host: str = "127.0.0.1",
    port: int = 8000,
    reviews_dir: Optional[Union[str, Path]] = None,
) -> None:
    import uvicorn

    app = create_app(artifact_path, reviews_dir=reviews_dir)
    print(f"Minarai Review Server: http://{host}:{port}")
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(prog="python -m minarai.review.server")
    parser.add_argument("path")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    run_server(args.path, host=args.host, port=args.port)
