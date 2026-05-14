from __future__ import annotations

import json
from pathlib import Path

from sbombom.core.models import Dependency
from sbombom.core.utils import build_purl, is_exact_version


def parse_package_json(file_path: Path) -> list[Dependency]:
    data = json.loads(file_path.read_text(encoding="utf-8-sig"))
    deps: list[Dependency] = []

    for section, scope, is_dev in [
        ("dependencies", "required", False),
        ("devDependencies", "optional", True),
    ]:
        for name, version in data.get(section, {}).items():
            is_exact = is_exact_version(version)
            deps.append(
                Dependency(
                    name=name,
                    version=version if is_exact else None,
                    ecosystem="npm",
                    language="javascript",
                    source_file=file_path.name,
                    purl=build_purl("npm", name, version if is_exact else None),
                    scope=scope,
                    constraint=None if is_exact else version,
                    properties={"devDependency": "true"} if is_dev else {},
                )
            )
    return deps


def parse_package_lock_json(file_path: Path) -> list[Dependency]:
    data = json.loads(file_path.read_text(encoding="utf-8-sig"))
    packages = data.get("packages", {})
    deps: list[Dependency] = []

    for key, pkg in packages.items():
        if key == "":
            continue
        name = pkg.get("name") or key.split("node_modules/")[-1]
        version = pkg.get("version")
        if not name:
            continue
        deps.append(
            Dependency(
                name=name,
                version=version,
                ecosystem="npm",
                language="javascript",
                source_file=file_path.name,
                purl=build_purl("npm", name, version),
            )
        )
    return deps
