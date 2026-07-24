from __future__ import annotations

import logging
import time
import typer
from .app import check_once
from .config import Settings
from .db import Store
from .notify import write_atom

app = typer.Typer(help="Rapid public-feed monitoring for plausible nova candidates")

@app.command()
def check():
    """Fetch all configured sources once."""
    logging.basicConfig(level=logging.INFO)
    result = check_once(Settings.from_env())
    typer.echo(result)

@app.command()
def run():
    """Continuously poll configured sources."""
    logging.basicConfig(level=logging.INFO)
    settings = Settings.from_env()
    while True:
        result = check_once(settings)
        typer.echo(result)
        time.sleep(max(1, settings.poll_minutes) * 60)

@app.command("rebuild-feed")
def rebuild_feed():
    settings = Settings.from_env()
    write_atom(Store(settings.database_path).recent(), settings.atom_path)
    typer.echo(settings.atom_path)
