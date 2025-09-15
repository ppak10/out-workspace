import importlib.metadata
import typer

from rich import print as rprint


def register_version(app: typer.Typer):
    @app.command()
    def version() -> None:
        """Show the installed version of `out-workspace` package."""
        try:
            version = importlib.metadata.version("out-workspace")
            rprint(f"✅ out-workspace version {version}")
        except importlib.metadata.PackageNotFoundError:
            rprint(
                "⚠️  [yellow]out-workspace version unknown (package not installed)[/yellow]"
            )
            raise typer.Exit()

    return version
