# metapkg/cli.py
import typer
from req_writer import integrate_with_cli

app = typer.Typer(
    name="metapkg",
    help="A CLI tool to manage Python project metadata and dependencies."
)

# Integrate the reqs command
integrate_with_cli(app)

if __name__ == "__main__":
    app()