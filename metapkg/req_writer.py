# metapkg/req_writer.py
"""
Module for generating and updating requirements.txt files based on 
installed packages in the current environment or from imports in project files.

This module allows users to generate a requirements.txt file without needing
to maintain it manually, regardless of whether the project uses pyproject.toml
or not.
"""

import sys
from importlib.metadata import distributions
from pathlib import Path
from typing import List, Tuple, Set
import email.parser

# Only import importlib_metadata for Python < 3.9
if sys.version_info < (3, 9):
    try:
        from importlib_metadata import distributions
    except ImportError:
        raise ImportError("importlib_metadata is required for Python < 3.9. Install it with 'pip install importlib_metadata'")

def get_installed_packages() -> List[Tuple[str, str]]:
    """
    Retrieve a list of installed packages and their versions, filtering for top-level (directly installed) packages.
    
    Returns:
        List of tuples containing (package_name, version).
    """
    try:
        packages = []
        dependency_set: Set[str] = set()  # Track packages that are dependencies
        all_packages = []  # Store all packages temporarily

        print("Debug: Checking installed packages...")
        for dist in distributions():
            pkg_name = dist.metadata['Name'].lower()
            version = dist.version
            
            # Store package info
            all_packages.append((pkg_name, version))
            
            # Locate metadata directory via dist.files
            metadata_path = None
            metadata_found = False
            if dist.files:
                for file in dist.files:
                    if file.name == 'METADATA':
                        metadata_path = Path(dist.locate_file(file)).parent
                        break
                if metadata_path and metadata_path.suffix in {'.dist-info', '.egg-info'}:
                    metadata_found = True
                    print(f"Debug: Package {pkg_name} (version {version}) - Metadata path: {metadata_path}")
                    
                    # Parse METADATA file for dependencies
                    metadata_file = metadata_path / 'METADATA'
                    if metadata_file.exists():
                        try:
                            with metadata_file.open('r', encoding='utf-8') as f:
                                metadata_content = f.read()
                                metadata = email.parser.Parser().parsestr(metadata_content)
                                requires = metadata.get_all('Requires-Dist', [])
                                for req in requires:
                                    # Extract package name from requirement (e.g., 'tomli (>=2.0.1)' -> 'tomli')
                                    dep_name = req.split(' ')[0].split(';')[0].lower()
                                    dependency_set.add(dep_name)
                                    print(f"Debug: Package {pkg_name} depends on {dep_name}")
                        except Exception as e:
                            print(f"Debug: Error parsing METADATA for {pkg_name}: {str(e)}")
                    
                    # Check INSTALLER file as secondary confirmation
                    installer_file = metadata_path / 'INSTALLER'
                    is_user_installed = False
                    if installer_file.exists():
                        try:
                            with installer_file.open('r', encoding='utf-8') as f:
                                installer = f.read().strip().lower()
                                print(f"Debug: INSTALLER content for {pkg_name}: '{installer}'")
                                is_user_installed = installer in {'pip', 'uv'}
                        except Exception as e:
                            print(f"Debug: Error reading INSTALLER for {pkg_name}: {str(e)}")
                    else:
                        is_user_installed = True  # No INSTALLER, assume user-installed
                        print(f"Debug: No INSTALLER for {pkg_name}, assuming user-installed")
            else:
                print(f"Debug: No dist.files for {pkg_name}, assuming user-installed")
                is_user_installed = True
                metadata_found = False

            print(f"Debug: Package {pkg_name} (version {version}) - Metadata found: {metadata_found}, User-installed: {is_user_installed}")

        # Filter for top-level packages (not in dependency_set)
        for pkg_name, version in all_packages:
            if pkg_name not in dependency_set:
                print(f"Debug: Package {pkg_name} is top-level (not a dependency)")
                packages.append((pkg_name, version))
            else:
                print(f"Debug: Package {pkg_name} is a dependency, excluding")

        print(f"Debug: Found {len(packages)} top-level packages: {packages}")
        return packages
    except RuntimeError as e:
        raise RuntimeError(f"Failed to retrieve installed packages: {str(e)}")

def generate_requirements_txt(
    output_path: str = "requirements.txt",
    exclude_stdlib: bool = True
) -> None:
    """
    Generate a requirements.txt file with installed packages and their versions.
    
    Args:
        output_path: Path to write the requirements.txt file.
        exclude_stdlib: If True, excludes standard library packages.
    
    Raises:
        PermissionError: If writing to the output file fails.
        RuntimeError: If package retrieval fails.
    """
    # Standard library packages to exclude
    stdlib_packages = {
        'argparse', 'ast', 'asyncio', 'base64', 'bisect', 'builtins',
        'calendar', 'collections', 'contextlib', 'copy', 'csv', 'datetime',
        'decimal', 'enum', 'functools', 'hashlib', 'heapq', 'io', 'itertools',
        'json', 'logging', 'math', 'os', 'pathlib', 'random', 're', 'shutil',
        'socket', 'stat', 'string', 'subprocess', 'sys', 'tempfile', 'textwrap',
        'threading', 'time', 'traceback', 'types', 'typing', 'urllib', 'uuid',
        'warnings', 'weakref', 'zlib'
    }

    try:
        packages = get_installed_packages()
        filtered_packages = []

        print(f"Debug: Processing {len(packages)} packages for requirements.txt")
        for pkg_name, version in sorted(packages):
            # Normalize package name (e.g., 'scikit-learn' -> 'scikit_learn' for comparison)
            normalized_name = pkg_name.replace('-', '_').lower()
            # Skip standard library packages or pip/setuptools if exclude_stdlib is True
            if exclude_stdlib and (normalized_name in stdlib_packages or
                                 pkg_name.lower() in {'pip', 'setuptools', 'wheel', 'importlib_metadata', 'metapkg'}):
                print(f"Debug: Skipping {pkg_name} - Excluded as stdlib or build tool")
                continue
            # Format package name to match PyPI conventions (e.g., scikit_learn -> scikit-learn)
            pypi_name = pkg_name.replace('_', '-')
            filtered_packages.append(f"{pypi_name}=={version}")
            print(f"Debug: Including {pypi_name}=={version} in requirements.txt")

        # Ensure the output directory exists
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Write to requirements.txt
        try:
            with output_file.open('w', encoding='utf-8') as f:
                f.write("# Generated by metapkg\n")
                for pkg in filtered_packages:
                    f.write(f"{pkg}\n")
            print(f"Debug: Wrote {len(filtered_packages)} packages to {output_path}")
        except PermissionError as e:
            raise PermissionError(f"Cannot write to {output_path}: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Failed to write requirements.txt: {str(e)}")

    except Exception as e:
        raise RuntimeError(f"Error generating requirements.txt: {str(e)}")

def integrate_with_cli(app):
    """
    Integrate the requirements.txt generation with the Typer CLI.
    
    Args:
        app: Typer app instance to register the command.
    """
    import typer

    @app.command("reqs")
    def reqs(
        output: str = typer.Option(
            "requirements.txt",
            "--output", "-o",
            help="Path to the output requirements.txt file"
        ),
        include_stdlib: bool = typer.Option(
            False,
            "--include-stdlib",
            help="Include standard library packages in requirements.txt"
        )
    ):
        """Generate a requirements.txt file from installed packages."""
        try:
            generate_requirements_txt(output_path=output, exclude_stdlib=not include_stdlib)
            typer.echo(f"Successfully generated {output}")
        except (PermissionError, RuntimeError) as e:
            typer.echo(f"Error: {str(e)}", err=True)
            raise typer.Exit(code=1)