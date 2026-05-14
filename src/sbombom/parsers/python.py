from __future__ import annotations

from pathlib import Path

from packaging.requirements import InvalidRequirement
from packaging.requirements import Requirement

from sbombom.core.models import Dependency
from sbombom.core.utils import build_purl, normalize_python_name


IGNORED_PREFIXES = ("-r", "--index-url", "--extra-index-url")


def _strip_inline_comment(line: str) -> str:
    for marker in (" #", "\t#"):
        if marker in line:
            return line.split(marker, 1)[0].strip()
    return line


def parse_requirements(file_path: Path) -> list[Dependency]:
    deps: list[Dependency] = []
    for raw_line in file_path.read_text(encoding="utf-8-sig").splitlines():
        line = _strip_inline_comment(raw_line.strip())
        if not line or line.startswith("#") or line.startswith(IGNORED_PREFIXES):
            continue

        try:
            req = Requirement(line)
        except InvalidRequirement:
            continue
        clean_name = normalize_python_name(req.name)
        exact = None
        constraint = None
        for spec in req.specifier:
            if spec.operator == "==":
                exact = spec.version
                break
        if not exact and str(req.specifier):
            constraint = str(req.specifier)

        purl = build_purl("pypi", clean_name, exact)
        deps.append(
            Dependency(
                name=clean_name,
                version=exact,
                ecosystem="pypi",
                language="python",
                source_file=file_path.name,
                purl=purl,
                constraint=constraint,
            )
        )
    return deps
