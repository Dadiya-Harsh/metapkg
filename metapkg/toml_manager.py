# metapkg/toml_manager.py
import toml  # for reading
from tomli_w import dump as toml_dump  # for writing
from pathlib import Path

PYPROJECT = "pyproject.toml"

def read_toml():
    if not Path(PYPROJECT).exists():
        return None
    with open(PYPROJECT, "r") as f:
        return toml.load(f)

def write_toml(data):
    with open(PYPROJECT, "w") as f:
        toml_dump(data, f)

def get_dependencies():
    data = read_toml()
    if data is None:
        return []
    return data.get("project", {}).get("dependencies", [])

def add_dependency(dep):
    data = read_toml()
    if data is None:
        raise FileNotFoundError("pyproject.toml not found. Run 'metapkg init' first.")
    deps = data.setdefault("project", {}).setdefault("dependencies", [])
    if dep not in deps:
        deps.append(dep)
        write_toml(data)
        return True
    return False

def init_project(name, description, author, version="0.1.0"):
    data = {
        "project": {
            "name": name,
            "version": version,
            "description": description,
            "authors": [{"name": author}],
            "dependencies": [],
            "requires-python": ">=3.8",
        },
        "build-system": {
            "requires": ["hatchling"],
            "build-backend": "hatchling.build",
        }
    }
    write_toml(data)