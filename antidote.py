#!/usr/bin/env python3
"""Antidote by PROOF — Sovereign Auth Gap Scanner."""

import click
from engine.ast_parser import scan_file
from engine.patch_generator import generate_patch
from events.emitter import emit


@click.group()
def cli():
    """Antidote: deterministic auth-gap scanner for Python web frameworks."""


@cli.command()
@click.argument("filepath")
def scan(filepath):
    """Scan a single Python file for unprotected routes."""
    findings = scan_file(filepath)
    if not findings:
        click.echo(f"[ANTIDOTE] No unprotected routes found in {filepath}")
        return

    click.echo(f"[ANTIDOTE] Found {len(findings)} unprotected route(s) in {filepath}:")

    with open(filepath) as f:
        lines = f.readlines()

    for finding in findings:
        click.echo(f"  CRITICAL: {finding['function']} at line {finding['line']}")
        patch = generate_patch(finding, lines)
        event_path = emit(finding, patch)
        click.echo(f"  -> Event emitted: {event_path}")


@cli.command()
@click.option("--dir", "watch_dir", default="src", help="Directory to watch")
def watch(watch_dir):
    """Watch a directory for Python file changes and scan continuously."""
    from cli.watch import start_watch
    start_watch(watch_dir)


if __name__ == "__main__":
    cli()
