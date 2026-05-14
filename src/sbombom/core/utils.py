from __future__ import annotations

import re
from urllib.parse import quote


_EXACT_VERSION_RE = re.compile(r"^v?\d+(?:\.\d+)*(?:[-+][0-9A-Za-z.-]+)?$")


def is_exact_version(version: str | None) -> bool:
    if not version:
        return False
    return bool(_EXACT_VERSION_RE.match(version))


def normalize_python_name(name: str) -> str:
    return name.split("[")[0].strip()


def build_purl(ecosystem: str, name: str, version: str | None = None) -> str:
    encoded_name = quote(name, safe="/")
    if ecosystem == "npm":
        encoded_name = encoded_name.replace("@", "%40")
    if version:
        return f"pkg:{ecosystem}/{encoded_name}@{version}"
    return f"pkg:{ecosystem}/{encoded_name}"
