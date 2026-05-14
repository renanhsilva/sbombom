from __future__ import annotations

from pathlib import Path

SUPPORTED_BY_LANGUAGE = {
    "python": [
        "requirements.txt",
        "requirements-dev.txt",
        "*requirements*.txt",
        "*constraints*.txt",
        "requirements/*.txt",
        "pyproject.toml",
        "Pipfile.lock",
        "poetry.lock",
    ],
    "javascript": [
        "package.json",
        "package-lock.json",
        "yarn.lock",
        "pnpm-lock.yaml",
    ],
    "java": [
        "pom.xml",
        "build.gradle",
        "build.gradle.kts",
        "gradle.lockfile",
    ],
    "dotnet": [
        "*.csproj",
        "packages.lock.json",
        "packages.config",
    ],
    "golang": [
        "go.mod",
        "go.sum",
    ],
}

SUPPORTED_PATTERNS = [
    pattern
    for patterns in SUPPORTED_BY_LANGUAGE.values()
    for pattern in patterns
]

IMPLEMENTED = {
    "requirements.txt",
    "requirements-dev.txt",
    "package.json",
    "package-lock.json",
    "pom.xml",
    "packages.config",
    "go.mod",
}

LANGUAGE_ALIASES = {
    "py": "python",
    "python": "python",
    "pypi": "python",
    "js": "javascript",
    "node": "javascript",
    "nodejs": "javascript",
    "npm": "javascript",
    "javascript": "javascript",
    "java": "java",
    "maven": "java",
    "cs": "dotnet",
    "csharp": "dotnet",
    "dotnet": "dotnet",
    ".net": "dotnet",
    "nuget": "dotnet",
    "go": "golang",
    "golang": "golang",
}


def normalize_languages(language_filter: str | None) -> set[str] | None:
    if not language_filter:
        return None

    languages: set[str] = set()
    for raw_item in language_filter.split(","):
        item = raw_item.strip().lower()
        if not item:
            continue
        language = LANGUAGE_ALIASES.get(item)
        if not language:
            supported = ", ".join(SUPPORTED_BY_LANGUAGE)
            raise ValueError(f"Linguagem nao suportada: {raw_item}. Use uma destas: {supported}.")
        languages.add(language)
    return languages or None


def file_language(file_path: Path) -> str | None:
    name = file_path.name
    if (
        name in {"requirements.txt", "requirements-dev.txt", "pyproject.toml", "Pipfile.lock", "poetry.lock"}
        or _is_python_requirements_file(file_path)
    ):
        return "python"
    if name in {"package.json", "package-lock.json", "yarn.lock", "pnpm-lock.yaml"}:
        return "javascript"
    if name in {"pom.xml", "build.gradle", "build.gradle.kts", "gradle.lockfile"}:
        return "java"
    if name.endswith(".csproj") or name in {"packages.lock.json", "packages.config"}:
        return "dotnet"
    if name in {"go.mod", "go.sum"}:
        return "golang"
    return None


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


def detect_files(repo_root: Path, language_filter: str | None = None) -> tuple[list[Path], list[Path]]:
    languages = normalize_languages(language_filter)
    patterns_to_search = SUPPORTED_PATTERNS
    if languages:
        patterns_to_search = [
            pattern
            for language in sorted(languages)
            for pattern in SUPPORTED_BY_LANGUAGE[language]
        ]

    detected: set[Path] = set()
    for pattern in patterns_to_search:
        detected.update(repo_root.rglob(pattern))

    implemented, not_implemented = [], []
    for p in sorted(detected):
        language = file_language(p)
        if languages and language not in languages:
            continue
        if p.name in IMPLEMENTED or p.suffix == ".csproj" or _is_python_requirements_file(p):
            implemented.append(p)
        else:
            not_implemented.append(p)
    return implemented, not_implemented
