from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

from sbombom.core.models import Dependency
from sbombom.core.utils import build_purl


def parse_csproj(file_path: Path) -> list[Dependency]:
    root = ET.fromstring(file_path.read_text(encoding="utf-8-sig"))
    deps: list[Dependency] = []
    for item in root.iter():
        if item.tag.split("}")[-1] != "PackageReference":
            continue
        include = item.attrib.get("Include") or item.attrib.get("Update")
        version = item.attrib.get("Version")
        if version is None:
            for child in item:
                if child.tag.split("}")[-1] == "Version":
                    version = (child.text or "").strip()
                    break
        if include:
            deps.append(
                Dependency(
                    name=include,
                    version=version,
                    ecosystem="nuget",
                    language="dotnet",
                    source_file=file_path.name,
                    purl=build_purl("nuget", include, version),
                )
            )
    return deps


def parse_packages_config(file_path: Path) -> list[Dependency]:
    root = ET.fromstring(file_path.read_text(encoding="utf-8-sig"))
    deps: list[Dependency] = []
    for item in root.findall("package"):
        pkg_id = item.attrib.get("id")
        version = item.attrib.get("version")
        if not pkg_id:
            continue
        deps.append(
            Dependency(
                name=pkg_id,
                version=version,
                ecosystem="nuget",
                language="dotnet",
                source_file=file_path.name,
                purl=build_purl("nuget", pkg_id, version),
            )
        )
    return deps
