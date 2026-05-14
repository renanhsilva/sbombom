from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

from sbombom.core.models import Dependency
from sbombom.core.utils import build_purl


def _tag_name(tag: str) -> str:
    return tag.split("}")[-1]


def parse_pom_xml(file_path: Path) -> list[Dependency]:
    root = ET.fromstring(file_path.read_text(encoding="utf-8-sig"))
    deps: list[Dependency] = []
    for dep in root.iter():
        if _tag_name(dep.tag) != "dependency":
            continue
        data = {_tag_name(child.tag): (child.text or "").strip() for child in dep}
        group = data.get("groupId")
        artifact = data.get("artifactId")
        version = data.get("version")
        scope = data.get("scope")
        if not group or not artifact:
            continue
        name = f"{group}:{artifact}"
        constraint = version if version and version.startswith("${") else None
        exact_version = None if constraint else version
        deps.append(
            Dependency(
                name=name,
                version=exact_version,
                ecosystem="maven",
                language="java",
                source_file=file_path.name,
                purl=build_purl("maven", f"{group}/{artifact}", exact_version),
                scope=scope,
                constraint=constraint,
            )
        )
    return deps
