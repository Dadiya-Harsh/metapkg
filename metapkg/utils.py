# metapkg/utils.py
import subprocess
import sys
from typing import Dict, List, Set
import typer
from metapkg.req_writer import get_installed_packages

def install_missing_dependencies(toml_data: Dict) -> None:
    """
    Install missing dependencies from pyproject.toml using pip.
    
    Args:
        toml_data: Dictionary containing TOML data.
    
    Raises:
        RuntimeError: If installation fails.
    """
    if "project" not in toml_data or "dependencies" not in toml_data["project"]:
        raise ValueError("Invalid pyproject.toml: Missing [project] or [project.dependencies]")
    
    dependencies = toml_data["project"]["dependencies"]
    if not dependencies:
        typer.echo("No dependencies to install.")
        return
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "install"] + dependencies, check=True)
        typer.echo("Successfully installed missing dependencies.")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to install dependencies: {str(e)}")

def get_untracked_packages(toml_data: Dict) -> List[str]:
    """
    Identify installed packages not listed in pyproject.toml.
    
    Args:
        toml_data: Dictionary containing TOML data.
    
    Returns:
        List of untracked package names with versions.
    """
    if "project" not in toml_data or "dependencies" not in toml_data["project"]:
        return []
    
    toml_deps = {dep.split("[")[0].split("<")[0].split(">")[0].split("=")[0].strip().lower()
                 for dep in toml_data["project"]["dependencies"]}
    installed_packages = {pkg_name: version for pkg_name, version in get_installed_packages()}
    
    return [f"{pkg_name}=={version}" for pkg_name, version in installed_packages.items()
            if pkg_name not in toml_deps]

def integrate_with_cli(app):
    """
    Integrate the sync command with the Typer CLI.
    
    Args:
        app: Typer app instance to register the command.
    """
    import typer
    from metapkg.toml_manager import read_pyproject_toml, add_dependency, write_pyproject_toml

    @app.command(name="sync")
    def sync(add_untracked: bool = typer.Option(False, "--add-untracked", help="Add untracked packages to pyproject.toml")):
        """Sync the environment with pyproject.toml dependencies."""
        try:
            toml_data = read_pyproject_toml()
            if toml_data is None:
                raise ValueError("pyproject.toml not found. Run 'metapkg init' first.")
            
            # Install missing dependencies
            install_missing_dependencies(toml_data)
            
            # Optionally add untracked packages
            if add_untracked:
                untracked = get_untracked_packages(toml_data)
                if untracked:
                    typer.echo("Untracked packages detected:")
                    for pkg in untracked:
                        typer.echo(f"- {pkg}")
                    if typer.confirm("Add these packages to pyproject.toml?"):
                        for pkg in untracked:
                            toml_data = add_dependency(toml_data, pkg)
                        write_pyproject_toml(toml_data)
                        typer.echo("Updated pyproject.toml with untracked packages.")
                else:
                    typer.echo("No untracked packages found.")
        except Exception as e:
            typer.echo(f"Error: {str(e)}", err=True)
            raise typer.Exit(code=1)