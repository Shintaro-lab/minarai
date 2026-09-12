import textwrap
from pathlib import Path

import pytest

VALID_ARTIFACT_YAML = textwrap.dedent(
    """\
    id: sample-auth-design
    type: design
    title: ユーザー認証設計
    status: draft

    sections:
      - id: overview
        title: 概要
        content: |
          本システムのユーザー認証方式について記載する。

      - id: authentication
        title: 認証方式
        content: |
          OpenID Connectを利用する。

          **Authorization Code Flow + PKCE** を採用する。
    """
)


@pytest.fixture
def valid_artifact_path(tmp_path: Path) -> Path:
    path = tmp_path / "sample-design.yaml"
    path.write_text(VALID_ARTIFACT_YAML, encoding="utf-8")
    return path


@pytest.fixture
def reviews_dir(tmp_path: Path) -> Path:
    directory = tmp_path / "reviews"
    directory.mkdir()
    return directory
