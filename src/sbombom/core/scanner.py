from __future__ import annotations

from pathlib import Path

from sbombom.core.models import Dependency
from sbombom.parsers.dotnet import parse_csproj, parse_packages_config
from sbombom.parsers.golang import parse_go_mod
from sbombom.parsers.java import parse_pom_xml
from sbombom.parsers.javascript import parse_package_json, parse_package_lock_json
from sbombom.parsers.python import parse_pyproject_toml, parse_requirements


def _is_python_requirements_file(file_path: Path) -> bool:
    name = file_path.name.lower()
    parent = file_path.parent.name.lower()
    return (
        file_path.suffix.lower() == ".txt"
        and (
            "requirements" in name
            or "constraints" in name
            or parent == "requirements"
        )
    )


def parse_file(file_path: Path) -> list[Dependency]:
    name = file_path.name
    if name in {"requirements.txt", "requirements-dev.txt"} or _is_python_requirements_file(file_path):
        return parse_requirements(file_path)
    if name == "pyproject.toml":
        return parse_pyproject_toml(file_path)
    if name == "package.json":
        return parse_package_json(file_path)
    if name == "package-lock.json":
        return parse_package_lock_json(file_path)
    if name == "pom.xml":
        return parse_pom_xml(file_path)
    if name.endswith(".csproj"):
        return parse_csproj(file_path)
    if name == "packages.config":
        return parse_packages_config(file_path)
    if name == "go.mod":
        return parse_go_mod(file_path)
    return []


def deduplicate(dependencies: list[Dependency]) -> list[Dependency]:
    unique: dict[str, Dependency] = {}
    for dep in dependencies:
        key = dep.purl or f"{dep.ecosystem}:{dep.name}:{dep.version}:{dep.source_file}"
        unique[key] = dep
    return sorted(unique.values(), key=lambda d: (d.ecosystem, d.name.lower(), d.version or ""))
