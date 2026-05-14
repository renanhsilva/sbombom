from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sbombom import __version__
from sbombom.core.models import Dependency


def dependency_to_component(dep: Dependency) -> dict:
    props = {
        "language": dep.language,
        "ecosystem": dep.ecosystem,
        "source_file": dep.source_file,
        **dep.properties,
    }
    if dep.constraint:
        props["constraint"] = dep.constraint
    if dep.scope:
        props["scope"] = dep.scope

    component = {
        "type": "library",
        "name": dep.name,
        "version": dep.version or "unknown",
        "properties": [{"name": k, "value": v} for k, v in props.items() if v],
    }
    if dep.purl:
        component["purl"] = dep.purl
        component["bom-ref"] = dep.purl
    return component


def build_bom(app_name: str, dependencies: list[Dependency]) -> dict:
    components = [dependency_to_component(d) for d in dependencies]
    return {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "serialNumber": f"urn:uuid:{uuid4()}",
        "version": 1,
        "metadata": {
            "timestamp": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            "tools": [{"vendor": "internal", "name": "SBOMBOM", "version": __version__}],
            "component": {
                "type": "application",
                "name": app_name,
                "version": "unknown",
            },
        },
        "components": components,
    }
