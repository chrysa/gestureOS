"""gestureos command-line interface.

Bootstrap stub. The real composition root (camera capture, modality engines,
context/resolver/OS-control wiring) lands in Step 5b of the construction plan.
"""

from __future__ import annotations

import click
from rich.console import Console

from gestureos import __version__

console = Console()


@click.group(invoke_without_command=True)
@click.version_option(__version__, prog_name="gestureos")
@click.pass_context
def main(ctx: click.Context) -> None:
    """Multi-screen eye & gesture computer control."""
    if ctx.invoked_subcommand is None:
        console.print(
            f"[bold]gestureos[/bold] {__version__} — bootstrap stub. Run [cyan]gestureos --help[/cyan] for commands."
        )


if __name__ == "__main__":  # pragma: no cover
    main()
