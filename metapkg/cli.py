# metapkg/cli.py
import typer
from req_writer import integrate_with_cli as integrate_reqs
from toml_manager import integrate_with_cli as integrate_toml
from import_scanner import integrate_with_cli as integrate_scan
from utils import integrate_with_cli as integrate_sync

app = typer.Typer(
    name="metapkg",
    help="A CLI tool to manage Python project metadata and dependencies.",
    add_completion=True
)

# Integrate all commands
integrate_reqs(app)
integrate_toml(app)
integrate_scan(app)
integrate_sync(app)

if __name__ == "__main__":
    app()