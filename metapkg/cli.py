# metapkg/cli.py
import typer
from metapkg.toml_manager import init_project, add_dependency
from metapkg.req_writer import write_requirements
from metapkg.import_scanner import suggest_missing_deps
from pathlib import Path

app = typer.Typer()

@app.command()
def init():
    """Initialize a new pyproject.toml."""
    if Path("pyproject.toml").exists():
        typer.echo("⚠️ pyproject.toml already exists.")
        return
    name = typer.prompt("Project name")
    desc = typer.prompt("Description")
    author = typer.prompt("Author name")
    init_project(name=name, description=desc, author=author)
    typer.echo("✅ Created pyproject.toml")

@app.command()
def add(package: str):
    """Add a dependency to pyproject.toml."""
    if add_dependency(package):
        typer.echo(f"✅ Added '{package}' to dependencies")
    else:
        typer.echo(f"📦 '{package}' is already in dependencies")

@app.command()
def reqs():
    """Generate requirements.txt from pyproject.toml."""
    write_requirements()

@app.command()
def scan():
    """Scan .py files for imports and suggest missing dependencies."""
    suggest_missing_deps()

if __name__ == "__main__":
    app()