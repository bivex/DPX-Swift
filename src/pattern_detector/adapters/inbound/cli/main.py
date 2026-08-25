"""Typer and Rich CLI interface for DPX-Swift."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from pattern_detector.adapters.outbound.persistence.llm_report_formatter import LlmReportFormatter
from pattern_detector.bootstrap.container import Container, create_container
from pattern_detector.domain.pattern import PATTERN_CATALOG
from pattern_detector.domain.value_objects import ConfidenceLevel, PatternCategory, PatternType
from pattern_detector.ports.inbound import ScanOptions

app = typer.Typer(
    name="dpx-swift",
    help="🍏 Protocol-Oriented Pattern Scanner, Actor Concurrency & SwiftUI Clean Architecture Static Analyzer (Swift 5.5 - 6.0+).",
    no_args_is_help=True,
)
console = Console()


@app.command()
def scan(
    path: Annotated[
        str,
        typer.Argument(
            help="Path to a Swift source file (.swift) or directory containing an Xcode project / Swift Package.",
        ),
    ] = ".",
    min_confidence: Annotated[
        float,
        typer.Option(
            "--min-confidence",
            "-c",
            help="Minimum confidence threshold (0.0 - 1.0).",
        ),
    ] = 0.0,
    pattern: Annotated[
        list[str] | None,
        typer.Option(
            "--pattern",
            "-p",
            help="Filter for specific pattern type(s) (e.g. 'actor_model_isolation', 'protocol_extension_default_impl', 'retain_cycle_strong_self').",
        ),
    ] = None,
    json_output: Annotated[
        str | None,
        typer.Option(
            "--json-output",
            "-J",
            help="Export findings to a JSON file.",
        ),
    ] = None,
    html_output: Annotated[
        str | None,
        typer.Option(
            "--html-output",
            "-H",
            help="Export interactive HTML architecture observability HUD.",
        ),
    ] = None,
    markdown_output: Annotated[
        str | None,
        typer.Option(
            "--markdown-output",
            "-M",
            help="Export findings to a Markdown report.",
        ),
    ] = None,
    sarif_output: Annotated[
        str | None,
        typer.Option(
            "--sarif-output",
            "-S",
            help="Export OASIS SARIF v2.1.0 file for GitHub Security / Code Scanning.",
        ),
    ] = None,
    llm: Annotated[
        bool,
        typer.Option(
            "--llm",
            help="Output structured AI architectural prompt context.",
        ),
    ] = False,
    exclude: Annotated[
        list[str] | None,
        typer.Option(
            "--exclude",
            "-e",
            help="Directory name(s) to exclude from scanning (e.g. -e Tests -e Pods).",
        ),
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option(
            "--verbose",
            "-v",
            help="Enable verbose output.",
        ),
    ] = False,
) -> None:
    """Scan a Swift codebase for Protocol-Oriented Patterns, Concurrency Actors, and Memory Safety Hazards."""
    target_path = str(Path(path).resolve())
    container = create_container()
    options = ScanOptions(
        min_confidence=min_confidence,
        enabled_patterns=pattern or [],
        output_json_path=json_output,
        output_html_path=html_output,
        output_markdown_path=markdown_output,
        output_sarif_path=sarif_output,
        exclude_dirs=exclude or [],
        verbose=verbose,
    )

    scanner = container.get_scanner()
    report = scanner.scan_path(target_path, options=options)

    if llm:
        formatter = LlmReportFormatter()
        print(formatter.format_scan_report(report))
    else:
        formatter = container.get_formatter()
        print(formatter.format(report, verbose=verbose))

        if html_output:
            console.print(f"[bold green]✔ Interactive HTML dashboard exported to:[/bold green] [cyan]{html_output}[/cyan]")
        if json_output:
            console.print(f"[bold green]✔ JSON findings exported to:[/bold green] [cyan]{json_output}[/cyan]")
        if markdown_output:
            console.print(f"[bold green]✔ Markdown report exported to:[/bold green] [cyan]{markdown_output}[/cyan]")
        if sarif_output:
            console.print(f"[bold green]✔ SARIF file exported to:[/bold green] [cyan]{sarif_output}[/cyan]")


@app.command()
def rules() -> None:
    """List all available Swift detection rules and architectural checks."""
    table = Table(
        title="🍏 DPX-Swift: Supported Pattern Rules & Quality Checks",
        title_style="bold orange3",
        border_style="dim",
    )
    table.add_column("Category", style="bold cyan")
    table.add_column("Pattern Type", style="bold white")
    table.add_column("Name", style="yellow")
    table.add_column("Description", style="dim")

    for ptype, pdef in PATTERN_CATALOG.items():
        table.add_row(
            pdef.category.value.upper(),
            ptype.value,
            pdef.name,
            pdef.description[:60] + "..." if len(pdef.description) > 60 else pdef.description,
        )

    console.print(table)


@app.command()
def info(
    pattern_name: Annotated[
        str,
        typer.Argument(
            help="Pattern type or name to query (e.g. 'actor_model_isolation', 'retain_cycle_strong_self').",
        ),
    ],
) -> None:
    """Display deep architectural details, rationale, and advice for a specific Swift pattern."""
    target_type: PatternType | None = None
    for ptype in PatternType:
        if ptype.value.lower() == pattern_name.lower():
            target_type = ptype
            break

    if not target_type:
        console.print(f"[bold red]Pattern '{pattern_name}' not found.[/bold red]")
        raise typer.Exit(code=1)

    pdef = PATTERN_CATALOG[target_type]
    panel = Panel.fit(
        f"[bold white]Pattern:[/bold white] [bold cyan]{pdef.name}[/bold cyan]\n"
        f"[bold white]Type Identifier:[/bold white] [yellow]{pdef.type.value}[/yellow]\n"
        f"[bold white]Category:[/bold white] {pdef.category.value.upper()}\n"
        f"[bold white]Swift Target:[/bold white] {pdef.swift_version}\n\n"
        f"[bold white]Description:[/bold white]\n{pdef.description}\n\n"
        f"[bold white]Architecture Recommendation:[/bold white]\n{pdef.recommendation or 'Adheres to standard Swift idiom.'}",
        title=f"🔍 Swift Architecture Encyclopedia: {pdef.name}",
        border_style="orange3",
    )
    console.print(panel)


def main() -> None:
    """CLI entrypoint."""
    app()


if __name__ == "__main__":
    main()
