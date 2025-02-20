import click
from rich.console import Console
from rich.table import Table
import csv
from pathlib import Path
import logging

from res import RESFile
from relay import RelayAutomation

console = Console()


@click.group()
def cli():
    pass


@cli.group()
def filters():
    """Commands for managing Relay subreddit filters."""
    pass


@filters.command(name="sync-all")
@click.argument(
    "res_backup", type=click.Path(), default="data/RES.json", required=False
)
@click.option("--device", help="Specific Android device ID to use")
@click.option(
    "--max-additions",
    default=None,
    type=int,
    help="Max number of subreddits to add (if not set, add all)",
)
def sync_filters(res_backup: str, device: str, max_additions: int):
    """Sync all subreddit filters from RES backup to Relay for Reddit."""
    ra = RelayAutomation(device)
    ra.sync_from_res(
        res_backup,
        csv_path="data/relay.csv",
        max_additions=max_additions,
    )
    console.print("[bold green]Sync complete![/bold green]")


@filters.command(name="add")
@click.argument("subreddits", type=str)
@click.option("--device", help="Specific Android device ID to use")
def add_filters(subreddits: str, device: str):
    """
    Add specific subreddit filters to Relay.

    Provide a comma-separated list of subreddits. Example:
      filters add "subreddit1, subreddit2"
    """
    sub_list = [s.strip() for s in subreddits.split(",") if s.strip()]
    ra = RelayAutomation(device)
    for sub in sub_list:
        success = ra.add_subreddit_filter(sub)
        if success:
            console.print(f"[green]Successfully added {sub}[/green]")
        else:
            console.print(f"[red]Failed to add {sub}[/red]")
    console.print("[bold]Finished processing filters.[/bold]")


@cli.command(name="status")
@click.argument(
    "res_backup", type=click.Path(), default="data/RES.json", required=False
)
@click.argument(
    "csv_file",
    type=click.Path(),
    default="data/relay.csv",
    required=False,
)
def show_status(res_backup: str, csv_file: str):
    """Show comparison between RES backup and Relay CSV filters."""
    logging.debug(f"Received res_backup: {res_backup}, csv_file: {csv_file}")
    if not Path(res_backup).exists():
        console.print(f"[red]File not found: {res_backup}[/red]")
        return
    if not Path(csv_file).exists():
        console.print(f"[red]CSV file not found: {csv_file}[/red]")
        return
    res_obj = RESFile(res_backup)
    res_subs = set(res_obj.extract_subreddits())

    # Load CSV subreddits
    def load_csv_subreddits(csv_path: str) -> list:
        subs = []
        with open(csv_path, newline="", encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile)
            next(reader, None)
            for row in reader:
                if row:
                    subs.append(row[0])
        return subs

    csv_subs = set(load_csv_subreddits(csv_file))
    only_in_res = res_subs - csv_subs
    only_in_csv = csv_subs - res_subs
    common = res_subs.intersection(csv_subs)

    table = Table(title="Subreddit Comparison")
    table.add_column("Category", style="cyan")
    table.add_column("Count", style="green")
    table.add_column("Subreddits", style="magenta")
    table.add_row(
        "Only in RES Backup",
        str(len(only_in_res)),
        ", ".join(sorted(only_in_res)) or "None",
    )
    table.add_row(
        "Only in OCR CSV",
        str(len(only_in_csv)),
        ", ".join(sorted(only_in_csv)) or "None",
    )
    table.add_row("In Both", str(len(common)), ", ".join(sorted(common)) or "None")
    console.print(table)


@cli.command(name="update-csv")
@click.option("--device", help="Specific Android device ID to use")
@click.option(
    "--max-iterations", default=5000, help="Max screenshot iterations for OCR"
)
def update_relay_csv(device: str, max_iterations: int):
    """
    Update the Relay CSV by scanning current filters.
    Uses OCR on Relay's filter screen to build an up-to-date CSV.
    """
    ra = RelayAutomation(device)
    ra.update_csv_with_subreddits(max_iterations)


if __name__ == "__main__":
    cli()
