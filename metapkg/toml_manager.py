# metapkg/toml_manager.py
# Use tomli and tomli_w for TOML parsing and writing (not the older 'toml' package)
import tomli
import tomli_w
from pathlib import Path
from typing import Dict, List, Optional
import typer
import re
import os

def get_project_root() -> Path:
    """
    Get the project root directory (where pyproject.toml is expected).
    
    Returns:
        Path object pointing to the project root directory.
    """
    # Assuming the script is in metapkg/metapkg/, go up two levels to the root
    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent
    return project_root

def validate_version_specifier(version: str) -> str:
    """
    Validate and normalize a Python version specifier to ensure PEP 440 compliance.
    
    Args:
        version: Version specifier (e.g., "3.12", ">=3.8").
    
    Returns:
        Normalized version specifier (e.g., ">=3.12").
    
    Raises:
        ValueError: If the version specifier is invalid.
    """
    # Valid PEP 440 operators
    valid_operators = {">=", "<=", "==", ">", "<", "~=", "!="}
    
    # Check if the version already includes an operator
    if any(version.startswith(op) for op in valid_operators):
        # Basic validation for version number (e.g., "3.12", "3.8.1")
        version_part = re.split(r"[><=~!]", version.lstrip("><=~!"))[-1].strip()
        if not re.match(r"^\d+\.\d+(\.\d+)?$", version_part):
            raise ValueError(f"Invalid version number in specifier: {version_part}")
        return version
    
    # If no operator, assume >= and validate version number
    if re.match(r"^\d+\.\d+(\.\d+)?$", version):
        return f">={version}"
    
    raise ValueError(f"Invalid version specifier: {version}. Use formats like '>=3.12' or '3.12'")

def create_pyproject_toml(
    project_name: str,
    version: str,
    description: str,
    author: str,
    license: str,
    python_version: str,
    build_backend: str
) -> Dict:
    """
    Create a minimal pyproject.toml structure.
    
    Args:
        project_name: Name of the project.
        version: Project version.
        description: Short project description.
        author: Author name.
        license: License type (e.g., MIT, Apache-2.0).
        python_version: Minimum Python version (e.g., ">=3.8").
        build_backend: Build backend (setuptools, hatchling, flit).
    
    Returns:
        Dictionary representing the pyproject.toml structure.
    """
    # Validate and normalize python_version
    python_version = validate_version_specifier(python_version)

    toml_data = {
        "project": {
            "name": project_name,
            "version": version,
            "description": description,
            "authors": [{"name": author}],
            "license": {"text": license},
            "requires-python": python_version,
            "dependencies": [],
            "readme": "README.md"
        },
        "build-system": {}
    }

    if build_backend == "setuptools":
        toml_data["build-system"] = {
            "requires": ["setuptools>=61.0"],
            "build-backend": "setuptools.build_meta"
        }
    elif build_backend == "hatchling":
        toml_data["build-system"] = {
            "requires": ["hatchling"],
            "build-backend": "hatchling.build"
        }
    elif build_backend == "flit":
        toml_data["build-system"] = {
            "requires": ["flit_core>=3.2"],
            "build-backend": "flit_core.buildapi"
        }
    else:
        raise ValueError(f"Unsupported build backend: {build_backend}")

    return toml_data

def write_pyproject_toml(toml_data: Dict, output_path: str = None) -> None:
    """
    Write the TOML data to a file.
    
    Args:
        toml_data: Dictionary containing TOML data.
        output_path: Path to write the pyproject.toml file (defaults to project root).
    
    Raises:
        PermissionError: If writing to the file fails.
    """
    if output_path is None:
        output_path = get_project_root() / "pyproject.toml"
    else:
        output_path = Path(output_path)
    
    try:
        with output_path.open("wb") as f:
            tomli_w.dump(toml_data, f)
    except PermissionError as e:
        raise PermissionError(f"Cannot write to {output_path}: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Failed to write pyproject.toml: {str(e)}")

def read_pyproject_toml(file_path: str = None) -> Optional[Dict]:
    """
    Read the pyproject.toml file from the project root by default.
    
    Args:
        file_path: Path to the pyproject.toml file (defaults to project root).
    
    Returns:
        Dictionary containing TOML data, or None if the file doesn't exist.
    
    Raises:
        RuntimeError: If reading or parsing the file fails.
    """
    if file_path is None:
        file_path = get_project_root() / "pyproject.toml"
    else:
        file_path = Path(file_path)
    
    if not file_path.exists():
        return None
    try:
        with file_path.open("rb") as f:
            return tomli.load(f)
    except tomli.TOMLDecodeError as e:
        # Extract line number and context from the error message if possible
        error_msg = str(e)
        line_info = ""
        if hasattr(e, "line") and e.line is not None:
            line_info = f" at line {e.line}"
        raise RuntimeError(f"Failed to parse {file_path}{line_info}: Invalid TOML syntax - {error_msg}")
    except Exception as e:
        raise RuntimeError(f"Failed to read {file_path}: {str(e)}")

def add_dependency(toml_data: Dict, package: str) -> Dict:
    """
    Add a package to [project.dependencies] in the TOML data.
    
    Args:
        toml_data: Dictionary containing TOML data.
        package: Package name to add (e.g., "requests").
    
    Returns:
        Updated TOML data.
    
    Raises:
        ValueError: If the project section is missing.
    """
    if "project" not in toml_data or "dependencies" not in toml_data["project"]:
        raise ValueError("Invalid pyproject.toml: Missing [project] or [project.dependencies]")
    
    # Normalize package name (e.g., requests>=2.28.1 -> requests)
    package_name = re.split("[><=~]", package)[0].strip()
    dependencies = toml_data["project"]["dependencies"]
    
    # Avoid duplicates (case-insensitive)
    if not any(dep.lower().startswith(package_name.lower()) for dep in dependencies):
        toml_data["project"]["dependencies"].append(package)
    
    return toml_data

def remove_dependency(toml_data: Dict, package: str) -> Dict:
    """
    Remove a package from [project.dependencies] in the TOML data.
    
    Args:
        toml_data: Dictionary containing TOML data.
        package: Package name to remove (e.g., "requests").
    
    Returns:
        Updated TOML data.
    
    Raises:
        ValueError: If the project section is missing.
    """
    if "project" not in toml_data or "dependencies" not in toml_data["project"]:
        raise ValueError("Invalid pyproject.toml: Missing [project] or [project.dependencies]")
    
    # Remove matching dependency (case-insensitive)
    toml_data["project"]["dependencies"] = [
        dep for dep in toml_data["project"]["dependencies"]
        if not dep.lower().startswith(package.lower())
    ]
    
    return toml_data

def check_publish_readiness(toml_data: Dict) -> List[str]:
    """
    Check if pyproject.toml is ready for PyPI publishing.
    
    Args:
        toml_data: Dictionary containing TOML data.
    
    Returns:
        List of warning messages for missing or invalid fields.
    """
    warnings = []
    
    if "project" not in toml_data:
        warnings.append("Missing [project] section")
        return warnings
    
    project = toml_data["project"]
    
    required_fields = ["name", "version", "description", "license", "authors"]
    for field in required_fields:
        if field not in project:
            warnings.append(f"Missing required field: {field}")
    
    if "requires-python" not in project:
        warnings.append("Missing recommended field: requires-python")
    
    if "readme" not in project:
        warnings.append("Missing recommended field: readme")
    
    if "classifiers" not in project or not project["classifiers"]:
        warnings.append("Missing recommended field: classifiers (useful for PyPI categorization)")
    
    if "urls" not in project:
        warnings.append("Missing recommended field: urls (e.g., Homepage, Documentation)")
    
    return warnings

def integrate_with_cli(app):
    """
    Integrate TOML management commands with the Typer CLI.
    
    Args:
        app: Typer app instance to register the commands.
    """
    import typer

    @app.command(name="init")
    def init():
        """Initialize a new pyproject.toml file interactively."""
        try:
            project_root = get_project_root()
            toml_path = project_root / "pyproject.toml"
            if toml_path.exists():
                if not typer.confirm(f"{toml_path} already exists. Overwrite?"):
                    typer.echo("Aborted.")
                    raise typer.Exit()
            
            project_name = typer.prompt("Project name", default="my-project")
            version = typer.prompt("Version", default="0.1.0")
            description = typer.prompt("Description", default="")
            author = typer.prompt("Author", default="")
            license = typer.prompt("License", default="MIT")
            python_version = typer.prompt(
                "Minimum Python version (e.g., >=3.8, ==3.12)",
                default=">=3.8"
            )
            build_backend = typer.prompt(
                "Build backend (setuptools, hatchling, flit)",
                default="setuptools",
                type=str,
                show_choices=True
            )
            
            toml_data = create_pyproject_toml(
                project_name=project_name,
                version=version,
                description=description,
                author=author,
                license=license,
                python_version=python_version,
                build_backend=build_backend
            )
            write_pyproject_toml(toml_data)
            typer.echo(f"Successfully created {toml_path}")
        except Exception as e:
            typer.echo(f"Error: {str(e)}", err=True)
            raise typer.Exit(code=1)

    @app.command(name="add")
    def add(package: str = typer.Argument(..., help="Package to add (e.g., requests>=2.28.1)")):
        """Add a package to pyproject.toml dependencies."""
        try:
            toml_data = read_pyproject_toml()
            if toml_data is None:
                raise ValueError("pyproject.toml not found in project root. Run 'metapkg init' first.")
            
            toml_data = add_dependency(toml_data, package)
            write_pyproject_toml(toml_data)
            typer.echo(f"Added {package} to pyproject.toml")
        except Exception as e:
            typer.echo(f"Error: {str(e)}", err=True)
            raise typer.Exit(code=1)

    @app.command(name="remove")
    def remove(package: str = typer.Argument(..., help="Package to remove (e.g., requests)")):
        """Remove a package from pyproject.toml dependencies."""
        try:
            toml_data = read_pyproject_toml()
            if toml_data is None:
                raise ValueError("pyproject.toml not found in project root. Run 'metapkg init' first.")
            
            toml_data = remove_dependency(toml_data, package)
            write_pyproject_toml(toml_data)
            typer.echo(f"Removed {package} from pyproject.toml")
        except Exception as e:
            typer.echo(f"Error: {str(e)}", err=True)
            raise typer.Exit(code=1)

    @app.command(name="check")
    def check():
        """Check if pyproject.toml is ready for PyPI publishing."""
        try:
            toml_data = read_pyproject_toml()
            if toml_data is None:
                raise ValueError("pyproject.toml not found in project root. Run 'metapkg init' first.")
            
            warnings = check_publish_readiness(toml_data)
            if not warnings:
                typer.echo("pyproject.toml is ready for PyPI publishing!")
            else:
                typer.echo("Warnings found in pyproject.toml:")
                for warning in warnings:
                    typer.echo(f"- {warning}")
        except Exception as e:
            typer.echo(f"Error: {str(e)}", err=True)
            raise typer.Exit(code=1)