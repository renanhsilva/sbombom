from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class Dependency:
    name: str
    version: str | None
    ecosystem: str
    language: str
    source_file: str
    purl: str | None = None
    scope: str | None = None
    constraint: str | None = None
    properties: dict[str, str] = field(default_factory=dict)
