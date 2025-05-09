# metapkg/req_writer.py
from metapkg.toml_manager import get_dependencies
from pathlib import Path

def write_requirements():
    deps = get_dependencies()
    if not deps:
        print("No dependencies found.")
        return
    with open("requirements.txt", "w") as f:
        for dep in deps:
            f.write(f"{dep}\n")
    print(f"✅ Wrote {len(deps)} dependencies to requirements.txt")