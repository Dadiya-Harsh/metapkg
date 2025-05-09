# metapkg/import_scanner.py
import ast
from pathlib import Path

def scan_imports():
    imports = set()
    for path in Path().rglob("*.py"):
        try:
            tree = ast.parse(path.read_text())
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name.split(".")[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module.split(".")[0])
        except Exception:
            continue
    return sorted(imports)

def suggest_missing_deps():
    from metapkg.toml_manager import get_dependencies
    installed = set(get_dependencies())
    scanned = set(scan_imports())
    missing = scanned - installed
    if missing:
        print("🔍 Suggested missing dependencies:")
        for dep in sorted(missing):
            print(f" - {dep}")
    else:
        print("🎉 All imports are covered in dependencies.")