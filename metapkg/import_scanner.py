# metapkg/import_scanner.py
import ast
import os
from pathlib import Path
from typing import Dict, List, Set
import typer

def get_top_level_imports(file_path: Path) -> Set[str]:
    """
    Extract top-level import names from a Python file.
    
    Args:
        file_path: Path to the Python file.
    
    Returns:
        Set of top-level import names.
    """
    try:
        with file_path.open("r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=str(file_path))
        
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.level == 0:  # Only absolute imports
                    imports.add(node.module.split(".")[0])
        
        return imports
    except Exception as e:
        typer.echo(f"Warning: Failed to parse {file_path}: {str(e)}", err=True)
        return set()

def scan_python_files(directory: Path = Path(".")) -> Set[str]:
    """
    Recursively scan .py files in a directory for top-level imports.
    
    Args:
        directory: Directory to scan.
    
    Returns:
        Set of all top-level import names found.
    """
    imports = set()
    for file_path in directory.rglob("*.py"):
        if file_path.is_file() and not file_path.name.startswith("."):
            imports.update(get_top_level_imports(file_path))
    return imports

# Mapping of common import names to package names
IMPORT_TO_PACKAGE: Dict[str, str] = {
    "requests": "requests",
    "flask": "flask",
    "django": "django",
    "pandas": "pandas",
    "numpy": "numpy",
    "matplotlib": "matplotlib",
    "sklearn": "scikit-learn",
    "torch": "torch",
    "tensorflow": "tensorflow",
    "pytest": "pytest",
    # Add more mappings as needed
}

def map_imports_to_packages(imports: Set[str]) -> Dict[str, str]:
    """
    Map import names to likely package names.
    
    Args:
        imports: Set of import names.
    
    Returns:
        Dictionary mapping import names to package names.
    """
    return {imp: IMPORT_TO_PACKAGE.get(imp, imp) for imp in imports if imp in IMPORT_TO_PACKAGE}

def get_missing_dependencies(imports: Set[str], toml_data: Dict) -> List[str]:
    """
    Identify imports not listed in pyproject.toml dependencies.
    
    Args:
        imports: Set of import names.
        toml_data: Dictionary containing TOML data.
    
    Returns:
        List of package names not in dependencies.
    """
    if "project" not in toml_data or "dependencies" not in toml_data["project"]:
        return []
    
    dependencies = {dep.split("[")[0].split("<")[0].split(">")[0].split("=")[0].strip().lower()
                    for dep in toml_data["project"]["dependencies"]}
    import_to_package = map_imports_to_packages(imports)
    return [pkg for imp, pkg in import_to_package.items() if pkg.lower() not in dependencies]

def integrate_with_cli(app):
    """
    Integrate the scan command with the Typer CLI.
    
    Args:
        app: Typer app instance to register the command.
    """
    import typer
    from toml_manager import read_pyproject_toml, add_dependency, write_pyproject_toml

    @app.command(name="scan")
    def scan(directory: str = typer.Option(".", "--dir", "-d", help="Directory to scan")):
        """Scan Python files for imports and suggest missing dependencies."""
        try:
            toml_data = read_pyproject_toml()
            if toml_data is None:
                raise ValueError("pyproject.toml not found. Run 'metapkg init' first.")
            
            imports = scan_python_files(Path(directory))
            if not imports:
                typer.echo("No imports found in Python files.")
                return
            
            missing_packages = get_missing_dependencies(imports, toml_data)
            if not missing_packages:
                typer.echo("All detected imports are listed in pyproject.toml.")
                return
            
            typer.echo("Missing dependencies detected:")
            for pkg in missing_packages:
                typer.echo(f"- {pkg}")
            
            if typer.confirm("Add missing dependencies to pyproject.toml?"):
                for pkg in missing_packages:
                    toml_data = add_dependency(toml_data, pkg)
                write_pyproject_toml(toml_data)
                typer.echo("Updated pyproject.toml with missing dependencies.")
        except Exception as e:
            typer.echo(f"Error: {str(e)}", err=True)
            raise typer.Exit(code=1)