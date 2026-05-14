from __future__ import annotations

import json
import sys
from pathlib import Path

import typer
from rich.console import Console

from sbombom.core.cyclonedx import build_bom
from sbombom.core.repo import infer_repo_name, prepare_repo
from sbombom.core.scanner import deduplicate, parse_file
from sbombom.detectors.files import detect_files, file_language, normalize_languages

app = typer.Typer(no_args_is_help=True)
console = Console()


def _normalize_references_args(args: list[str]) -> list[str]:
    normalized: list[str] = []
    index = 0

    while index < len(args):
        token = args[index]
        if token != "--referencias":
            normalized.append(token)
            index += 1
            continue

        normalized.append(token)
        index += 1
        first_value = True
        while index < len(args) and not args[index].startswith("--"):
            if not first_value:
                normalized.append("--referencias")
            normalized.append(args[index])
            first_value = False
            index += 1

    return normalized


@app.command()
def main(
    repo: str | None = typer.Option(None, "--repo", help="Caminho local ou URL Git"),
    app_name: str | None = typer.Option(None, "--app", help="Nome da aplicacao"),
    referencias: list[str] | None = typer.Option(None, "--referencias", help="Arquivos de referencia"),
    language: str | None = typer.Option(
        None,
        "--language",
        "-l",
        help="Filtra por linguagem/ecossistema: python, javascript, java, dotnet ou golang",
    ),
    output: str | None = typer.Option(None, "--output", help="Arquivo de saida JSON"),
    output_format: str = typer.Option("cyclonedx-json", "--format", help="Formato de saida"),
    fail_on_empty: bool = typer.Option(False, "--fail-on-empty", help="Falha se nao houver componentes"),
    verbose: bool = typer.Option(False, "--verbose", help="Logs detalhados"),
) -> None:
    if output_format != "cyclonedx-json":
        raise typer.BadParameter("Apenas --format cyclonedx-json e suportado neste MVP.")

    try:
        selected_languages = normalize_languages(language)
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc

    if not repo and not (app_name and referencias):
        raise typer.BadParameter("Informe --repo OU --app junto com --referencias.")
    if repo and referencias:
        raise typer.BadParameter("Use --repo OU --app com --referencias, nao ambos.")

    temp_dir = None
    files_to_parse: list[Path] = []

    try:
        if repo:
            try:
                repo_root, temp_dir = prepare_repo(repo)
            except ValueError as exc:
                raise typer.BadParameter(str(exc)) from exc
            if verbose:
                console.print(f"[cyan]Analisando repositorio:[/cyan] {repo_root}")
                if selected_languages:
                    console.print(f"[cyan]Filtro de linguagem:[/cyan] {', '.join(sorted(selected_languages))}")
            implemented, not_implemented = detect_files(repo_root, language)
            files_to_parse = implemented
            if not app_name:
                app_name = infer_repo_name(repo, repo_root)
            if verbose:
                for p in not_implemented:
                    console.print(f"[yellow]Ignorado (nao implementado no MVP):[/yellow] {p}")
        else:
            app_name = app_name or "unknown-app"
            files_to_parse = [Path(p).resolve() for p in (referencias or [])]
            if selected_languages:
                files_to_parse = [
                    p for p in files_to_parse
                    if file_language(p) in selected_languages
                ]

        dependencies = []
        for file_path in files_to_parse:
            if not file_path.exists():
                if verbose:
                    console.print(f"[yellow]Arquivo nao encontrado:[/yellow] {file_path}")
                continue
            try:
                parsed = parse_file(file_path)
            except Exception as exc:
                if repo:
                    if verbose:
                        console.print(f"[yellow]Ignorado (erro ao analisar):[/yellow] {file_path}: {exc}")
                    continue
                raise typer.BadParameter(f"Erro ao analisar {file_path}: {exc}") from exc
            if verbose:
                console.print(f"[green]{file_path}[/green]: {len(parsed)} dependencias")
            dependencies.extend(parsed)

        dependencies = deduplicate(dependencies)
        bom = build_bom(app_name or "unknown-app", dependencies)

        if not dependencies:
            console.print("[yellow]Nenhum componente foi encontrado.[/yellow]")
            if fail_on_empty:
                raise typer.Exit(code=2)

        output_json = json.dumps(bom, indent=2, ensure_ascii=False)
        if output:
            Path(output).write_text(output_json + "\n", encoding="utf-8")
            console.print(f"[green]SBOM salvo em:[/green] {output}")
        else:
            print(output_json)
    finally:
        if temp_dir is not None:
            temp_dir.cleanup()


def run() -> None:
    app(args=_normalize_references_args(sys.argv[1:]))


if __name__ == "__main__":
    run()
