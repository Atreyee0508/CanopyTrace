"""Command Line Interface (CLI) for CanopyTrace with Rich terminal formatting."""

import json
from pathlib import Path
from typing import Optional
import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import print as rprint

from canopytrace.core.pipeline import run_forensic_pipeline
from canopytrace.db import seed_database, get_all_smuggling_patterns
from canopytrace.dossier import compile_evidentiary_dossier
from canopytrace.escalation import list_pending_escalations, approve_and_ingest_novel_finding
from canopytrace.schemas import ShippingManifest, PhysicalInspection

console = Console()


@click.group()
@click.version_option(version="0.1.0", prog_name="canopytrace")
def main() -> None:
    """CanopyTrace: AI Forensic Fingerprinting for Illegal Wildlife & Timber Trade Verification."""
    pass


@main.command()
@click.option("--manifest", required=True, type=click.Path(exists=True), help="Path to manifest JSON file.")
@click.option("--inspection", required=True, type=click.Path(exists=True), help="Path to physical inspection JSON file.")
@click.option("--case-id", default=None, help="Optional custom case ID.")
@click.option("--outdir", default=None, help="Directory to export compiled dossier files.")
def inspect(manifest: str, inspection: str, case_id: Optional[str], outdir: Optional[str]) -> None:
    """Run full forensic triage on a manifest and physical inspection."""
    with console.status("[bold green]Executing CanopyTrace Forensic Verification Pipeline..."):
        with open(manifest, "r", encoding="utf-8") as f:
            manifest_obj = ShippingManifest.model_validate(json.load(f))

        with open(inspection, "r", encoding="utf-8") as f:
            inspection_obj = PhysicalInspection.model_validate(json.load(f))

        out_path = Path(outdir) if outdir else None
        res = run_forensic_pipeline(manifest_obj, inspection_obj, case_id=case_id, output_dir=out_path)

    # Format result output
    discrepancy = res["discrepancy_score"]
    status_style = "bold red" if discrepancy >= 0.70 else ("bold yellow" if discrepancy >= 0.30 else "bold green")
    status_label = "CRITICAL SEIZURE ALERT" if discrepancy >= 0.70 else (
        "ELEVATED UNCERTAINTY" if discrepancy >= 0.30 else "CLEARED"
    )

    console.print()
    console.print(Panel(
        f"[bold]Case ID:[/bold] {res['case_id']}\n"
        f"[{status_style}]Status: {status_label}[/{status_style}]\n"
        f"[bold]Discrepancy Score:[/bold] {discrepancy:.2f} / 1.00\n"
        f"[bold]Suspected Taxon:[/bold] {res['suspected_species']} (CITES App {res['cites_appendix']})\n"
        f"[bold]Alert Dispatched:[/bold] {'🚨 YES' if res['alert_dispatched'] else 'NO'}\n"
        f"[bold]Dossier Package:[/bold] {res['dossier_package']['pdf_path']}\n"
        f"[bold]SHA-256 Digest:[/bold] {res['dossier_package']['sha256_hash']}",
        title="🌿 CanopyTrace Forensic Triage Verdict",
        border_style="cyan"
    ))

    # Print Contradictions Table
    flags = res["flagged_indicators"]
    if flags:
        table = Table(title="Contradictions & Red Flags", style="red")
        table.add_column("Indicator", style="bold yellow")
        for flag in flags:
            table.add_row(flag)
        console.print(table)

    # Statutory Non-Definitive Legal Disclaimer
    console.print(f"\n[dim italic]{res['forensic_output'].legal_disclaimer}[/dim italic]\n")


@main.group()
def db() -> None:
    """Manage offline reference database."""
    pass


@db.command("seed")
def seed_cmd() -> None:
    """Seed or rebuild the offline SQLite reference database."""
    with console.status("[bold blue]Seeding reference database from JSON/YAML sources..."):
        seed_database()
    console.print("[bold green]✔ Reference database seeded successfully.[/bold green]")


@main.group()
def patterns() -> None:
    """Inspect documented wildlife trafficking modus operandi."""
    pass


@patterns.command("list")
def patterns_list() -> None:
    """List all registered smuggling patterns."""
    mos = get_all_smuggling_patterns()
    table = Table(title="Documented Wildlife Trafficking Modus Operandi (MOs)")
    table.add_column("ID", style="bold cyan")
    table.add_column("Name", style="bold white")
    table.add_column("Category", style="yellow")
    table.add_column("Target Contraband", style="green")
    table.add_column("Risk", style="magenta")

    for mo in mos:
        table.add_row(mo["id"], mo["name"], mo["category"], mo["target_contraband"], f"{mo['risk_weight']:.2f}")
    console.print(table)


@main.group()
def escalate() -> None:
    """Manage novel anomaly escalations and scientific authority approvals."""
    pass


@escalate.command("list")
def escalate_list() -> None:
    """List pending novel anomaly escalation cases."""
    pending = list_pending_escalations()
    if not pending:
        console.print("[bold green]No pending escalation cases.[/bold green]")
        return

    table = Table(title="Pending Scientific Authority Escalations")
    table.add_column("Case ID", style="bold cyan")
    table.add_column("Checkpoint", style="white")
    table.add_column("Created At", style="yellow")
    table.add_column("Reason", style="red")

    for c in pending:
        table.add_row(c["case_id"], c["checkpoint_location"], c["created_at"], c["reason"])
    console.print(table)


@escalate.command("approve")
@click.argument("case_id")
@click.option("--species", required=True, help="Verified scientific binomial.")
@click.option("--appendix", required=True, type=click.Choice(["I", "II", "III", "None"]), help="CITES Appendix.")
@click.option("--notes", default="Verified by Higher Scientific Authority", help="Review comments.")
@click.option("--common-names", default=None, help="Comma-separated common names.")
def escalate_approve(case_id: str, species: str, appendix: str, notes: str, common_names: Optional[str]) -> None:
    """Approve a novel specimen finding and update the offline reference database."""
    cn = [c.strip() for c in common_names.split(",")] if common_names else [species]
    success = approve_and_ingest_novel_finding(
        case_id=case_id,
        verified_species=species,
        verified_appendix=appendix,
        authority_notes=notes,
        common_names=cn,
    )
    if success:
        console.print(f"[bold green]✔ Case {case_id} approved. New taxon '{species}' ingested into reference database![/bold green]")
    else:
        console.print(f"[bold red]Failed to approve case {case_id}.[/bold red]")


@main.group()
def dossier() -> None:
    """Manage evidentiary dossiers."""
    pass


@dossier.command("compile")
@click.option("--case-file", required=True, type=click.Path(exists=True), help="Path to case data JSON.")
@click.option("--outdir", default="./output", help="Output directory.")
def dossier_compile(case_file: str, outdir: str) -> None:
    """Compile multi-format dossier from case JSON."""
    with open(case_file, "r", encoding="utf-8") as f:
        case_data = json.load(f)
    meta = compile_evidentiary_dossier(case_data, Path(outdir))
    console.print(f"[bold green]✔ Dossier compiled:[/bold green] {meta['pdf_path']}")
    console.print(f"[bold cyan]SHA-256 Digest:[/bold cyan] {meta['sha256_hash']}")


@main.command()
@click.option("--host", default="127.0.0.1", help="Server host IP.")
@click.option("--port", default=8000, help="Server port number.")
def serve(host: str, port: int) -> None:
    """Launch CanopyTrace local Web UI dashboard and REST API."""
    import uvicorn
    from canopytrace.web.app import app
    console.print(f"[bold green]🌿 Starting CanopyTrace Web Dashboard on http://{host}:{port}[/bold green]")
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
