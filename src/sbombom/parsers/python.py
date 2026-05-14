from __future__ import annotations

import tomllib
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


def _dependency_from_requirement(
    line: str,
    source_file: str,
    *,
    scope: str | None = None,
    properties: dict[str, str] | None = None,
) -> Dependency | None:
    try:
        req = Requirement(line)
    except InvalidRequirement:
        return None

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
    return Dependency(
        name=clean_name,
        version=exact,
        ecosystem="pypi",
        language="python",
        source_file=source_file,
        purl=purl,
        scope=scope,
        constraint=constraint,
        properties=properties or {},
    )


def parse_requirements(file_path: Path) -> list[Dependency]:
    deps: list[Dependency] = []
    for raw_line in file_path.read_text(encoding="utf-8-sig").splitlines():
        line = _strip_inline_comment(raw_line.strip())
        if not line or line.startswith("#") or line.startswith(IGNORED_PREFIXES):
            continue

        dep = _dependency_from_requirement(line, file_path.name)
        if dep:
            deps.append(dep)
    return deps


def parse_pyproject_toml(file_path: Path) -> list[Dependency]:
    data = tomllib.loads(file_path.read_text(encoding="utf-8-sig"))
    deps: list[Dependency] = []

    project = data.get("project", {})
    for item in project.get("dependencies", []) or []:
        dep = _dependency_from_requirement(str(item), file_path.name, scope="required")
        if dep:
            deps.append(dep)

    optional_dependencies = project.get("optional-dependencies", {}) or {}
    for group, requirements in optional_dependencies.items():
        for item in requirements or []:
            dep = _dependency_from_requirement(
                str(item),
                file_path.name,
                scope="optional",
                properties={
                    "optionalDependency": "true",
                    "optionalDependencyGroup": str(group),
                },
            )
            if dep:
                deps.append(dep)
    return deps
