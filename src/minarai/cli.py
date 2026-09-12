"""``minarai`` command-line entry point.

Subcommands are dispatched manually (rather than via one big argparse
subparser tree) so that ``minarai review <path>`` (start the server) and
``minarai review list|update ...`` can share the ``review`` prefix without
argparse's positional/subparser ambiguity.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from minarai.artifacts.loader import load_artifact
from minarai.artifacts.validator import ArtifactValidationError
from minarai.review import store
from minarai.review.models import VALID_STATUSES
from minarai.review.server import run_server


def _print_validation_error(path: str, exc: ArtifactValidationError) -> None:
    print(f"Invalid artifact: {path}", file=sys.stderr)
    for error in exc.errors:
        print(f"  - {error}", file=sys.stderr)


def _cmd_artifact_validate(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="minarai artifact validate")
    parser.add_argument("path")
    args = parser.parse_args(argv)

    try:
        artifact = load_artifact(args.path)
    except ArtifactValidationError as exc:
        _print_validation_error(args.path, exc)
        return 1

    print(f"OK: {args.path} ({artifact.id}) is a valid artifact")
    return 0


def _dispatch_artifact(argv: list[str]) -> int:
    if argv and argv[0] == "validate":
        return _cmd_artifact_validate(argv[1:])
    print("Usage: minarai artifact validate <path>", file=sys.stderr)
    return 1


def _cmd_review_start(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="minarai review")
    parser.add_argument("path")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args(argv)

    run_server(args.path, host=args.host, port=args.port)
    return 0


def _cmd_review_list(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="minarai review list")
    parser.add_argument("path")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    try:
        artifact = load_artifact(args.path)
    except ArtifactValidationError as exc:
        _print_validation_error(args.path, exc)
        return 1

    comments = store.list_comments(artifact.id)

    if args.json:
        print(json.dumps([c.to_dict() for c in comments], ensure_ascii=False, indent=2))
        return 0

    print(f"Artifact: {artifact.id}\n")
    for comment in comments:
        print(f"[{comment.id}]")
        print(f"Section: {comment.target}")
        print(f"Status: {comment.status}")
        print()
        print(comment.comment.strip())
        print()
    return 0


def _cmd_review_update(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="minarai review update")
    parser.add_argument("comment_id")
    parser.add_argument("--status", required=True, choices=list(VALID_STATUSES))
    args = parser.parse_args(argv)

    try:
        comment = store.update_comment_status(args.comment_id, args.status)
    except store.ReviewError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Updated {comment.id} -> {comment.status}")
    return 0


def _dispatch_review(argv: list[str]) -> int:
    if argv and argv[0] == "list":
        return _cmd_review_list(argv[1:])
    if argv and argv[0] == "update":
        return _cmd_review_update(argv[1:])
    if not argv:
        print(
            "Usage: minarai review <path> | minarai review list <path> "
            "| minarai review update <id> --status <status>",
            file=sys.stderr,
        )
        return 1
    return _cmd_review_start(argv)


def main(argv: Optional[list[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        print("Usage: minarai <artifact|review> ...", file=sys.stderr)
        return 1

    command, rest = argv[0], argv[1:]
    if command == "artifact":
        return _dispatch_artifact(rest)
    if command == "review":
        return _dispatch_review(rest)

    print(f"Unknown command: {command}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
