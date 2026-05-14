from __future__ import annotations

import tempfile
from pathlib import PurePosixPath
from pathlib import Path
from urllib.parse import urlparse

from git import Repo


def is_git_url(value: str) -> bool:
    return value.startswith(("http://", "https://", "git@", "ssh://"))


def infer_repo_name(repo: str, repo_root: Path) -> str:
    if not is_git_url(repo):
        return repo_root.name

    value = repo.rstrip("/")
    if value.startswith("git@") and ":" in value:
        value = value.rsplit(":", 1)[1]
    else:
        value = urlparse(value).path

    name = PurePosixPath(value).name
    if name.endswith(".git"):
        name = name[:-4]
    return name or repo_root.name


def prepare_repo(repo: str) -> tuple[Path, tempfile.TemporaryDirectory[str] | None]:
    path = Path(repo)
    if path.exists() and path.is_dir():
        return path.resolve(), None

    if is_git_url(repo):
        tmp = tempfile.TemporaryDirectory(prefix="sbombom-")
        try:
            Repo.clone_from(
                repo,
                tmp.name,
                multi_options=["--depth=1"],
                env={
                    "GIT_CONFIG_COUNT": "1",
                    "GIT_CONFIG_KEY_0": "core.longpaths",
                    "GIT_CONFIG_VALUE_0": "true",
                },
            )
            return Path(tmp.name), tmp
        except Exception as exc:
            tmp.cleanup()
            detail = (getattr(exc, "stderr", None) or str(exc)).strip()
            message = f"Nao foi possivel clonar o repositorio: {repo}"
            if detail:
                message = f"{message}. Detalhe: {detail}"
            raise ValueError(message) from exc

    raise ValueError(f"Repositorio invalido: {repo}")
