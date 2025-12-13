"""
EdgeFinder Command Line Interface
Interactive CLI with comprehensive safety prompts and EQ12 integration
"""

import asyncio
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm
from rich.table import Table

from .config import load_config
from .models import SearchCriteria, SourceType
from .scorer import RepositoryScorer
from .search_github import GitHubSearcher
from .search_huggingface import HuggingFaceSearcher

console = Console()
logger = logging.getLogger(__name__)


class EdgeFinderCLI:
    """Main CLI application class"""

    def __init__(self, config_path: Path | None = None):
        self.config = load_config(config_path)
        self.console = Console()

        # Setup logging
        logging.basicConfig(
            level=getattr(logging, self.config.log_level.upper()),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

        # Create output directories
        Path(self.config.output_dir).mkdir(parents=True, exist_ok=True)
        Path(self.config.downloads_dir).mkdir(parents=True, exist_ok=True)

    def _display_legal_notice(self):
        """Display legal and ethical usage notice"""
        notice = Panel.fit(
            """[bold red]⚠️ LEGAL NOTICE ⚠️[/bold red]

This tool accesses only [bold]PUBLIC[/bold] content. By using EdgeFinder, you agree to:

• [green]✓[/green] Only access public repositories and APIs
• [green]✓[/green] Respect rate limits and terms of service  
• [green]✓[/green] Verify license compatibility before code reuse
• [green]✓[/green] Get explicit permission before redistributing code
• [red]✗[/red] Never attempt to access private or restricted content
• [red]✗[/red] Never bypass authentication or security measures

[bold yellow]Always review generated patches and suggestions manually![/bold yellow]""",
            title="EdgeFinder - Ethical Repository Analysis",
            border_style="red",
        )
        console.print(notice)
        console.print()

    def _display_search_summary(self, candidates, criteria):
        """Display search results summary"""
        table = Table(title="🔍 Search Results Summary")

        table.add_column("Source", style="cyan")
        table.add_column("Candidates", justify="right", style="green")
        table.add_column("Top Score", justify="right", style="yellow")
        table.add_column("License Compatible", justify="right", style="blue")

        # Group by source
        by_source = {}
        for candidate in candidates:
            source = candidate.source.value
            if source not in by_source:
                by_source[source] = []
            by_source[source].append(candidate)

        total_candidates = 0
        for source, source_candidates in by_source.items():
            compatible_count = len(
                [
                    c
                    for c in source_candidates
                    if c.license_info and c.license_info.compatibility.value == "compatible"
                ]
            )

            top_score = max([c.score for c in source_candidates], default=0.0)

            table.add_row(
                source.title(),
                str(len(source_candidates)),
                f"{top_score:.1f}",
                str(compatible_count),
            )
            total_candidates += len(source_candidates)

        console.print(table)

        # Display search criteria
        criteria_panel = Panel(
            f"""[bold]Keywords:[/bold] {', '.join(criteria.keywords)}
[bold]Languages:[/bold] {', '.join(criteria.languages) if criteria.languages else 'Any'}
[bold]Min Stars:[/bold] {criteria.min_stars}
[bold]Sources:[/bold] {', '.join([s.value for s in criteria.sources])}
[bold]License Filter:[/bold] {', '.join(criteria.license_allowlist) if criteria.license_allowlist else 'Any'}""",
            title="Search Criteria",
        )
        console.print(criteria_panel)

        return total_candidates

    def _display_candidate_details(self, candidates, limit: int = 10):
        """Display detailed candidate information"""
        table = Table(title="📊 Top Candidates", show_lines=True)

        table.add_column("Rank", width=4)
        table.add_column("Repository", style="cyan")
        table.add_column("Description", max_width=40)
        table.add_column("Score", justify="right", style="yellow")
        table.add_column("Stars", justify="right", style="green")
        table.add_column("License", style="blue")
        table.add_column("Updated", style="magenta")

        for i, candidate in enumerate(candidates[:limit], 1):
            # Format description
            desc = candidate.description or "No description"
            if len(desc) > 37:
                desc = desc[:34] + "..."

            # Format update time
            updated = "Unknown"
            if candidate.stats.updated_at:
                days_ago = (
                    datetime.now(candidate.stats.updated_at.tzinfo) - candidate.stats.updated_at
                ).days
                if days_ago == 0:
                    updated = "Today"
                elif days_ago == 1:
                    updated = "Yesterday"
                else:
                    updated = f"{days_ago}d ago"

            # Format license
            license_name = "Unknown"
            license_style = "dim"
            if candidate.license_info:
                license_name = (
                    candidate.license_info.name or candidate.license_info.spdx_id or "Unknown"
                )
                if candidate.license_info.compatibility.value == "compatible":
                    license_style = "green"
                elif candidate.license_info.compatibility.value == "incompatible":
                    license_style = "red"
                else:
                    license_style = "yellow"

            table.add_row(
                str(i),
                f"[link={candidate.url}]{candidate.full_name}[/link]",
                desc,
                f"{candidate.score:.1f}",
                str(candidate.stats.stars),
                f"[{license_style}]{license_name}[/{license_style}]",
                updated,
            )

        console.print(table)

    async def _search_repositories(self, criteria: SearchCriteria) -> list:
        """Search repositories from all configured sources"""
        candidates = []

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:

            # GitHub search
            if SourceType.GITHUB in criteria.sources:
                task = progress.add_task("Searching GitHub repositories...", total=None)
                try:
                    async with GitHubSearcher(self.config) as github_searcher:
                        github_candidates = await github_searcher.search_repositories(criteria)
                        candidates.extend(github_candidates)
                        progress.update(task, description=f"GitHub: {len(github_candidates)} found")
                except Exception as e:
                    console.print(f"[red]GitHub search failed: {e}[/red]")
                    progress.update(task, description="GitHub: Failed")

            # Hugging Face search
            if SourceType.HUGGINGFACE in criteria.sources:
                task = progress.add_task("Searching Hugging Face repositories...", total=None)
                try:
                    async with HuggingFaceSearcher(self.config) as hf_searcher:
                        hf_candidates = await hf_searcher.search_repositories(criteria)
                        candidates.extend(hf_candidates)
                        progress.update(
                            task, description=f"Hugging Face: {len(hf_candidates)} found"
                        )
                except Exception as e:
                    console.print(f"[red]Hugging Face search failed: {e}[/red]")
                    progress.update(task, description="Hugging Face: Failed")

        return candidates


@click.group()
@click.option(
    "--config", type=click.Path(exists=True, path_type=Path), help="Configuration file path"
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
@click.option("--debug", is_flag=True, help="Enable debug logging")
@click.pass_context
def cli(ctx, config, verbose, debug):
    """
    EdgeFinder - Ethical Repository Reconnaissance Tool

    Discover public GitHub and Hugging Face repositories for EQ12 system enhancement.
    """
    # Setup context
    ctx.ensure_object(dict)

    # Load configuration
    cli_instance = EdgeFinderCLI(config)
    if verbose:
        cli_instance.config.verbose = True
    if debug:
        cli_instance.config.debug = True
        logging.getLogger().setLevel(logging.DEBUG)

    ctx.obj["cli"] = cli_instance

    # Display legal notice for interactive commands
    if ctx.invoked_subcommand in ["search", "analyze", "download", "patch"]:
        cli_instance._display_legal_notice()


@cli.command()
@click.option("--keywords", required=True, help="Search keywords (space or comma separated)")
@click.option("--lang", "--languages", help="Programming languages (comma separated)")
@click.option("--min-stars", default=0, type=int, help="Minimum star count")
@click.option("--max", "--max-results", default=50, type=int, help="Maximum results per source")
@click.option("--since", type=click.DateTime(), help="Only repos updated since date (YYYY-MM-DD)")
@click.option("--license-allowlist", help="Allowed licenses (comma separated)")
@click.option(
    "--sources", default="github,huggingface", help="Sources to search (github,huggingface)"
)
@click.option(
    "--output", "-o", type=click.Path(path_type=Path), help="Output file for results (JSON)"
)
@click.option("--score-min", default=0.0, type=float, help="Minimum score threshold")
@click.option("--eq12-integration", help="EQ12 integration type (betting, ai, analytics)")
@click.pass_context
def search(
    ctx,
    keywords,
    lang,
    min_stars,
    max,
    since,
    license_allowlist,
    sources,
    output,
    score_min,
    eq12_integration,
):
    """Search public repositories based on criteria."""

    cli_instance = ctx.obj["cli"]

    try:
        # Parse search criteria
        keyword_list = [k.strip() for k in keywords.replace(",", " ").split() if k.strip()]
        language_list = [l.strip() for l in lang.split(",")] if lang else []
        license_list = (
            [l.strip() for l in license_allowlist.split(",")] if license_allowlist else []
        )
        source_list = [SourceType(s.strip()) for s in sources.split(",")]

        criteria = SearchCriteria(
            keywords=keyword_list,
            languages=language_list,
            min_stars=min_stars,
            max_results_per_source=max,
            updated_since=since,
            license_allowlist=license_list,
            sources=source_list,
        )

        # Enhance keywords for EQ12 integration
        if eq12_integration:
            if eq12_integration == "betting":
                criteria.keywords.extend(cli_instance.config.eq12_integration.betting_keywords)
            elif eq12_integration == "ai":
                criteria.keywords.extend(cli_instance.config.eq12_integration.ai_keywords)
            elif eq12_integration == "analytics":
                criteria.keywords.extend(cli_instance.config.eq12_integration.analytics_keywords)

        # Run search
        console.print("[bold green]🔍 Searching repositories...[/bold green]")
        candidates = asyncio.run(cli_instance._search_repositories(criteria))

        if not candidates:
            console.print("[yellow]No repositories found matching criteria.[/yellow]")
            return

        # Score and rank candidates
        scorer = RepositoryScorer(cli_instance.config)
        ranked_candidates = scorer.rank_candidates(candidates, criteria)

        # Filter by minimum score
        if score_min > 0:
            ranked_candidates = scorer.filter_candidates_by_score(ranked_candidates, score_min)

        # Display results
        total_found = cli_instance._display_search_summary(ranked_candidates, criteria)

        if ranked_candidates:
            cli_instance._display_candidate_details(ranked_candidates)

            # Generate dashboard URLs
            dashboard_info = Panel(
                f"""[bold]EQ12 Dashboard URLs:[/bold]
🔗 Search Results: {cli_instance.config.get_dashboard_url('edgefinder_search_results.html')}
📊 Analysis Dashboard: {cli_instance.config.get_dashboard_url('edgefinder_analysis.html')}
🔒 Security Dashboard: {cli_instance.config.get_dashboard_url('edgefinder_security.html')}""",
                title="Dashboard Integration",
            )
            console.print(dashboard_info)

        # Save results if requested
        if output:
            results_data = {
                "search_criteria": criteria.dict(),
                "candidates": [candidate.dict() for candidate in ranked_candidates],
                "total_found": total_found,
                "timestamp": datetime.utcnow().isoformat(),
                "dashboard_urls": {
                    "search_results": cli_instance.config.get_dashboard_url(
                        "edgefinder_search_results.html"
                    ),
                    "analysis": cli_instance.config.get_dashboard_url("edgefinder_analysis.html"),
                    "security": cli_instance.config.get_dashboard_url("edgefinder_security.html"),
                },
            }

            output.write_text(json.dumps(results_data, indent=2, default=str))
            console.print(f"[green]Results saved to: {output}[/green]")

    except Exception as e:
        console.print(f"[red]Search failed: {e}[/red]")
        if cli_instance.config.debug:
            console.print_exception()
        sys.exit(1)


@cli.command()
@click.option("--candidate", help="Single candidate ID to analyze")
@click.option(
    "--input",
    "input_file",
    type=click.Path(exists=True, path_type=Path),
    help="JSON file with candidates",
)
@click.option("--top", type=int, help="Analyze only top N candidates")
@click.option("--download", is_flag=True, help="Download repositories for analysis")
@click.option("--security-scan", is_flag=True, help="Run security analysis")
@click.option("--generate-patch", is_flag=True, help="Generate integration patches")
@click.option(
    "--output", "-o", type=click.Path(path_type=Path), help="Output file for analysis results"
)
@click.pass_context
def analyze(ctx, candidate, input_file, top, download, security_scan, generate_patch, output):
    """Perform detailed analysis of candidates."""

    ctx.obj["cli"]

    # Implementation would continue here with analysis logic
    console.print("[yellow]Analysis command implementation in progress...[/yellow]")


@cli.command()
@click.option("--candidate-ids", help="Comma-separated candidate IDs")
@click.option(
    "--input",
    "input_file",
    type=click.Path(exists=True, path_type=Path),
    help="JSON file with candidates",
)
@click.option("--output-dir", type=click.Path(path_type=Path), help="Download directory")
@click.option("--format", "download_format", default="zip", help="Download format (zip, tar.gz)")
@click.option("--concurrent", default=3, type=int, help="Maximum concurrent downloads")
@click.pass_context
def download(ctx, candidate_ids, input_file, output_dir, download_format, concurrent):
    """Download repositories for offline analysis."""

    ctx.obj["cli"]

    # Safety confirmation
    if not Confirm.ask("⚠️ This will download external code. Continue?", default=False):
        console.print("[yellow]Download cancelled.[/yellow]")
        return

    console.print("[yellow]Download command implementation in progress...[/yellow]")


@cli.command()
@click.option("--candidate", help="Candidate to patch")
@click.option(
    "--input",
    "input_file",
    type=click.Path(exists=True, path_type=Path),
    help="Analysis results file",
)
@click.option(
    "--patch-type",
    default="wrapper",
    type=click.Choice(["wrapper", "enhancement", "update"]),
    help="Type of patch",
)
@click.option("--target-integration", default="eq12", help="Integration target")
@click.option(
    "--output", "-o", type=click.Path(path_type=Path), help="Output directory for patches"
)
@click.option("--dry-run", is_flag=True, help="Show patches without creating files")
@click.pass_context
def patch(ctx, candidate, input_file, patch_type, target_integration, output, dry_run):
    """Generate safe integration patches."""

    ctx.obj["cli"]

    # Safety confirmation
    if not dry_run and not Confirm.ask(
        "⚠️ This will generate code patches. Continue?", default=False
    ):
        console.print("[yellow]Patch generation cancelled.[/yellow]")
        return

    console.print("[yellow]Patch command implementation in progress...[/yellow]")


@cli.command()
@click.option(
    "--input",
    "input_file",
    type=click.Path(exists=True, path_type=Path),
    help="Analysis results file",
)
@click.option(
    "--format",
    "report_format",
    default="markdown",
    type=click.Choice(["json", "markdown", "html"]),
    help="Output format",
)
@click.option("--include-patches", is_flag=True, help="Include patch summaries")
@click.option("--include-security", is_flag=True, help="Include security analysis")
@click.option(
    "--template", type=click.Path(exists=True, path_type=Path), help="Custom report template"
)
@click.option("--out", type=click.Path(path_type=Path), help="Output file")
@click.pass_context
def report(ctx, input_file, report_format, include_patches, include_security, template, out):
    """Generate comprehensive reports."""

    ctx.obj["cli"]

    console.print("[yellow]Report command implementation in progress...[/yellow]")


@cli.command()
@click.pass_context
def version(ctx):
    """Show version information."""
    from . import __version__

    console.print(
        Panel.fit(
            f"""[bold cyan]EdgeFinder[/bold cyan] v{__version__}
[dim]Ethical Repository Reconnaissance Tool[/dim]

[bold]EQ12 Integration:[/bold] ✓ Enabled
[bold]Dashboard URL:[/bold] https://eq12.local/dashboards/edgefinder.html
[bold]License:[/bold] MIT
[bold]Author:[/bold] EQ12 Development Team""",
            title="Version Information",
        )
    )


def main():
    """Main CLI entry point"""
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user.[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]Unexpected error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
