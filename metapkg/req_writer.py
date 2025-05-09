# metapkg/req_writer.py
"""
Module for generating and updating requirements.txt files based on 
installed packages in the current environment or from imports in project files.

This module allows users to generate a requirements.txt file without needing
to maintain it manually, regardless of whether the project uses pyproject.toml
or not.
"""

import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union

# Import detection and package mapping utilities
import ast
import importlib.metadata
import pkgutil
from collections import defaultdict
import toml


class RequirementsWriter:
    """Class to generate and update requirements.txt files."""
    
    def __init__(self, project_dir: str = '.', verbose: bool = False):
        """
        Initialize the RequirementsWriter.
        
        Args:
            project_dir: Path to the project directory
            verbose: Whether to print verbose output
        """
        self.project_dir = Path(project_dir).resolve()
        self.verbose = verbose
        
        # Path to the requirements.txt file
        self.requirements_path = self.project_dir / 'requirements.txt'
        
        # Standard library modules (to exclude from requirements)
        self.stdlib_modules = self._get_stdlib_modules()
        
        # Map of import names to package names
        self.import_to_package_map = self._build_import_package_map()
    
    def _get_stdlib_modules(self) -> Set[str]:
        """Get a set of standard library module names."""
        stdlib_modules = set()
        
        # Get standard library modules using pkgutil
        for _, name, is_pkg in pkgutil.iter_modules():
            if is_pkg:
                stdlib_modules.add(name)
        
        # Add built-in modules
        stdlib_modules.update(sys.builtin_module_names)
        
        # Add common standard library modules that might not be caught above
        stdlib_modules.update([
            'abc', 'argparse', 'ast', 'asyncio', 'collections', 'configparser',
            'contextlib', 'copy', 'csv', 'datetime', 'decimal', 'enum', 'functools',
            'glob', 'hashlib', 'http', 'inspect', 'io', 'itertools', 'json', 'logging',
            'math', 'multiprocessing', 'os', 'pathlib', 'pickle', 'random', 're',
            'shutil', 'signal', 'socket', 'sqlite3', 'ssl', 'string', 'subprocess',
            'sys', 'tempfile', 'threading', 'time', 'traceback', 'typing', 'unittest',
            'urllib', 'uuid', 'warnings', 'xml', 'zipfile'
        ])
        
        return stdlib_modules
    
    def _build_import_package_map(self) -> Dict[str, str]:
        """Build a mapping from import names to package names."""
        # Start with common mappings that might not follow the standard pattern
        manual_mappings = {
            'numpy': 'numpy',
            'np': 'numpy',
            'pandas': 'pandas',
            'pd': 'pandas',
            'matplotlib': 'matplotlib',
            'plt': 'matplotlib',
            'sklearn': 'scikit-learn',
            'torch': 'torch',
            'tf': 'tensorflow',
            'cv2': 'opencv-python',
            'bs4': 'beautifulsoup4',
            'dotenv': 'python-dotenv',
            'yaml': 'pyyaml',
            'PIL': 'pillow',
            'flask': 'flask',
            'django': 'django',
            'requests': 'requests',
            'boto3': 'boto3',
            'sqlalchemy': 'sqlalchemy',
            'pytest': 'pytest',
            'fastapi': 'fastapi',
            'typer': 'typer',
            'click': 'click',
            'rich': 'rich',
            'tomli': 'tomli',
            'tomli_w': 'tomli-w',
            'toml': 'toml',
            'uvicorn': 'uvicorn',
            'pydantic': 'pydantic',
            'redis': 'redis',
            'psycopg2': 'psycopg2-binary',
            'pymongo': 'pymongo',
            'jwt': 'pyjwt',
            'cryptography': 'cryptography',
            'unittest': None,  # Standard library
            'mock': 'pytest-mock',
            'json': None,  # Standard library
            'os': None,  # Standard library
            'sys': None,  # Standard library
            're': None,  # Standard library
            'math': None,  # Standard library
            'datetime': None,  # Standard library
            'collections': None,  # Standard library
            'typing': None,  # Standard library
            'pathlib': None,  # Standard library
            'shutil': None,  # Standard library
            'subprocess': None,  # Standard library
            'argparse': None,  # Standard library
            'logging': None,  # Standard library
            'time': None,  # Standard library
        }
        
        # Try to add mappings from installed packages
        try:
            for dist in importlib.metadata.distributions():
                pkg_name = dist.metadata['Name']
                if pkg_name:
                    # Add the package name itself as a mapping
                    manual_mappings[pkg_name.lower()] = pkg_name
                    
                    # Try to find the top-level modules provided by this package
                    try:
                        top_level_txt = dist.read_text('top_level.txt')
                        if top_level_txt:
                            for module in top_level_txt.splitlines():
                                if module.strip():
                                    manual_mappings[module.strip().lower()] = pkg_name
                    except Exception:
                        # If we can't read top_level.txt, just continue
                        pass
        except Exception as e:
            # If there's an error while reading package metadata, just continue with what we have
            if self.verbose:
                print(f"Warning: Error while building import-to-package map: {e}")
        
        return manual_mappings
    
    def _get_installed_packages(self, direct_only: bool = True) -> Dict[str, str]:
        """
        Get information about installed packages.
        
        Args:
            direct_only: If True, only return direct dependencies (requires pip-chill)
        
        Returns:
            Dictionary mapping package names to their versions
        """
        packages = {}
        
        try:
            if direct_only:
                # Try to use pip-chill to get only direct dependencies
                try:
                    output = subprocess.check_output(
                        [sys.executable, '-m', 'pip_chill', '--no-version'],
                        universal_newlines=True
                    )
                    
                    # If pip-chill worked, get versions for the packages it returned
                    pkg_names = [line.split('==')[0].strip() for line in output.strip().split('\n') if line.strip()]
                    
                    for pkg_name in pkg_names:
                        try:
                            version = importlib.metadata.version(pkg_name)
                            packages[pkg_name] = version
                        except importlib.metadata.PackageNotFoundError:
                            # If we can't get the version, just include the package name
                            packages[pkg_name] = ''
                    
                except (subprocess.SubprocessError, FileNotFoundError):
                    # If pip-chill fails, fall back to using pip freeze
                    direct_only = False
                    if self.verbose:
                        print("Warning: pip-chill not found, falling back to pip freeze.")
            
            if not direct_only:
                # Use pip freeze to get all installed packages
                output = subprocess.check_output(
                    [sys.executable, '-m', 'pip', 'freeze'],
                    universal_newlines=True
                )
                
                for line in output.strip().split('\n'):
                    if not line or line.startswith('#'):
                        continue
                    
                    # Handle different formats: package==version, package @ file://path, etc.
                    if '==' in line:
                        pkg_name, version = line.split('==', 1)
                        packages[pkg_name.strip()] = version.strip()
                    elif ' @ ' in line:
                        pkg_name = line.split(' @ ')[0].strip()
                        packages[pkg_name] = ''  # Can't determine version for editable installs
                    else:
                        # Add the package without version info
                        packages[line.strip()] = ''
        
        except Exception as e:
            if self.verbose:
                print(f"Error getting installed packages: {e}")
        
        return packages
    
    def _scan_imports(self, include_dev: bool = False) -> Set[str]:
        """
        Scan the project for Python imports.
        
        Args:
            include_dev: Whether to include dev-related files (tests, etc.)
            
        Returns:
            Set of imported module names
        """
        imports = set()
        
        for py_file in self._find_python_files(include_dev):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse the Python file
                try:
                    tree = ast.parse(content)
                    
                    # Find all import statements
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for name in node.names:
                                # Get the root module (before any dots)
                                root_module = name.name.split('.')[0]
                                imports.add(root_module)
                                
                        elif isinstance(node, ast.ImportFrom):
                            if node.module:
                                # Get the root module (before any dots)
                                root_module = node.module.split('.')[0]
                                imports.add(root_module)
                
                except SyntaxError:
                    # If there's a syntax error in the file, just skip it
                    if self.verbose:
                        print(f"Warning: Syntax error in {py_file}, skipping import detection.")
            
            except Exception as e:
                if self.verbose:
                    print(f"Error processing {py_file}: {e}")
        
        return imports
    
    def _find_python_files(self, include_dev: bool = False) -> List[Path]:
        """
        Find all Python files in the project.
        
        Args:
            include_dev: Whether to include dev-related files (tests, etc.)
            
        Returns:
            List of paths to Python files
        """
        py_files = []
        
        # Directories to exclude
        exclude_dirs = {'.git', '.hg', '.svn', '__pycache__', '.eggs', '*.egg-info', 'dist', 'build', 'venv', '.venv', 'env', '.env'}
        if not include_dev:
            exclude_dirs.update({'tests', 'test', '.tox', '.github', '.gitlab', '.circleci'})
        
        for root, dirs, files in os.walk(self.project_dir):
            # Modify dirs in-place to skip excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs and not any(pattern in d for pattern in exclude_dirs if '*' in pattern)]
            
            for file in files:
                if file.endswith('.py'):
                    py_files.append(Path(root) / file)
        
        return py_files
    
    def _get_package_version(self, package_name: str) -> str:
        """Get the installed version of a package."""
        try:
            return importlib.metadata.version(package_name)
        except importlib.metadata.PackageNotFoundError:
            return ''
    
    def _map_imports_to_packages(self, imports: Set[str]) -> Dict[str, str]:
        """
        Map import names to package names with versions.
        
        Args:
            imports: Set of import names
            
        Returns:
            Dictionary mapping package names to versions
        """
        packages = {}
        
        for import_name in imports:
            # Skip standard library modules
            if import_name in self.stdlib_modules:
                continue
            
            # Look up the package name from our mapping
            package_name = self.import_to_package_map.get(import_name.lower())
            
            if package_name:
                version = self._get_package_version(package_name)
                packages[package_name] = version
        
        return packages
    
    def generate_from_environment(self, direct_only: bool = True) -> Dict[str, str]:
        """
        Generate requirements from the current Python environment.
        
        Args:
            direct_only: If True, try to include only direct dependencies
            
        Returns:
            Dictionary mapping package names to versions
        """
        return self._get_installed_packages(direct_only)
    
    def generate_from_imports(self, include_dev: bool = False) -> Dict[str, str]:
        """
        Generate requirements by scanning Python files for imports.
        
        Args:
            include_dev: Whether to include imports from test files
            
        Returns:
            Dictionary mapping package names to versions
        """
        imports = self._scan_imports(include_dev)
        return self._map_imports_to_packages(imports)
    
    def generate_from_pyproject(self) -> Dict[str, str]:
        """
        Generate requirements from pyproject.toml if it exists.
        
        Returns:
            Dictionary mapping package names to versions
        """
        pyproject_path = self.project_dir / 'pyproject.toml'
        packages = {}
        
        if not pyproject_path.exists():
            return packages
        
        try:
            with open(pyproject_path, 'rb') as f:
                pyproject_data = toml.load(f)
            
            # Get dependencies from pyproject.toml
            dependencies = pyproject_data.get('project', {}).get('dependencies', [])
            
            for dep in dependencies:
                # Extract the package name from the dependency string
                # Handle different formats: package, package>=1.0, package==1.0, etc.
                match = re.match(r'^([a-zA-Z0-9_.-]+)', dep)
                if match:
                    pkg_name = match.group(1)
                    # Try to get the actual installed version
                    version = self._get_package_version(pkg_name)
                    packages[pkg_name] = version
        
        except Exception as e:
            if self.verbose:
                print(f"Error reading pyproject.toml: {e}")
        
        return packages
    
    def write_requirements(self, packages: Dict[str, str], output_path: Optional[Path] = None) -> Path:
        """
        Write packages to a requirements.txt file.
        
        Args:
            packages: Dictionary mapping package names to versions
            output_path: Optional custom path for the output file
            
        Returns:
            Path to the written file
        """
        output_path = output_path or self.requirements_path
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# This file was generated by metapkg\n")
            f.write("# https://github.com/yourusername/metapkg\n\n")
            
            for pkg_name, version in sorted(packages.items()):
                if version:
                    f.write(f"{pkg_name}=={version}\n")
                else:
                    f.write(f"{pkg_name}\n")
        
        return output_path
    
    def update_requirements(self, 
                            method: str = 'auto', 
                            direct_only: bool = True,
                            include_dev: bool = False,
                            output_path: Optional[Path] = None) -> Path:
        """
        Update or create a requirements.txt file.
        
        Args:
            method: How to determine requirements:
                   'auto' - Use pyproject.toml if available, otherwise scan imports
                   'env' - Use installed packages
                   'imports' - Scan project files for imports
                   'pyproject' - Use pyproject.toml dependencies
            direct_only: For 'env' method, whether to include only direct dependencies
            include_dev: For 'imports' method, whether to include test files
            output_path: Optional custom path for the output file
            
        Returns:
            Path to the updated file
        """
        # Determine which method to use
        if method == 'auto':
            pyproject_path = self.project_dir / 'pyproject.toml'
            if pyproject_path.exists():
                method = 'pyproject'
            else:
                method = 'imports'
        
        # Get packages based on the chosen method
        if method == 'env':
            packages = self.generate_from_environment(direct_only)
        elif method == 'imports':
            packages = self.generate_from_imports(include_dev)
        elif method == 'pyproject':
            packages = self.generate_from_pyproject()
        else:
            raise ValueError(f"Unknown method: {method}")
        
        # Write the requirements file
        return self.write_requirements(packages, output_path)


def generate_requirements(
    project_dir: str = '.', 
    method: str = 'auto',
    direct_only: bool = True,
    include_dev: bool = False,
    output_path: Optional[str] = None,
    verbose: bool = False
) -> str:
    """
    Generate or update requirements.txt file.
    
    Args:
        project_dir: Path to the project directory
        method: How to determine requirements:
               'auto' - Use pyproject.toml if available, otherwise scan imports
               'env' - Use installed packages
               'imports' - Scan project files for imports
               'pyproject' - Use pyproject.toml dependencies
        direct_only: For 'env' method, whether to include only direct dependencies
        include_dev: For 'imports' method, whether to include test files
        output_path: Optional custom path for the output file
        verbose: Whether to print verbose output
        
    Returns:
        Path to the generated file
    """
    writer = RequirementsWriter(project_dir, verbose)
    
    output_path_obj = Path(output_path) if output_path else None
    result_path = writer.update_requirements(
        method=method,
        direct_only=direct_only,
        include_dev=include_dev,
        output_path=output_path_obj
    )
    
    if verbose:
        print(f"Requirements file written to: {result_path}")
    
    return str(result_path)


if __name__ == "__main__":
    # Simple CLI wrapper for testing
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate requirements.txt file")
    parser.add_argument("--project-dir", "-d", default=".", help="Project directory path")
    parser.add_argument(
        "--method", "-m", 
        choices=["auto", "env", "imports", "pyproject"], 
        default="auto",
        help="Method to determine requirements"
    )
    parser.add_argument(
        "--direct-only", 
        action="store_true", 
        help="Include only direct dependencies (for 'env' method)"
    )
    parser.add_argument(
        "--include-dev", 
        action="store_true", 
        help="Include test files (for 'imports' method)"
    )
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--verbose", "-v", action="store_true", help="Print verbose output")
    
    args = parser.parse_args()
    
    result = generate_requirements(
        project_dir=args.project_dir,
        method=args.method,
        direct_only=args.direct_only,
        include_dev=args.include_dev,
        output_path=args.output,
        verbose=args.verbose
    )
    
    print(f"Generated: {result}")