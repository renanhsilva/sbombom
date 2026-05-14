from __future__ import annotations

from pathlib import Path

from sbombom.core.models import Dependency
from sbombom.core.utils import build_purl


def parse_go_mod(file_path: Path) -> list[Dependency]:
    deps: list[Dependency] = []
    in_block = False
    for raw in file_path.read_text(encoding="utf-8-sig").splitlines():
        line = raw.split("//")[0].strip()
        if not line:
            continue
        if line.startswith("require ("):
            in_block = True
            continue
        if in_block and line == ")":
            in_block = False
            continue

        if line.startswith("require "):
            parts = line.replace("require ", "", 1).split()
        elif in_block:
            parts = line.split()
        else:
            continue

        if len(parts) < 2:
            continue
        module, version = parts[0], parts[1]
        deps.append(
            Dependency(
                name=module,
                version=version,
                ecosystem="golang",
                language="golang",
                source_file=file_path.name,
                purl=build_purl("golang", module, version),
            )
        )
    return deps
