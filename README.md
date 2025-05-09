# metapkg – Simplify Python Project Metadata Management

`metapkg` is a simple, fast, and intuitive CLI tool to help you manage your Python project metadata with ease. Whether you're starting a new project or maintaining an existing one, `metapkg` streamlines:

- Creating and updating `pyproject.toml`
- Adding/removing dependencies
- Scanning source files to suggest imports
- Auto-generating `requirements.txt`
- Preparing your package for publishing

No more manual edits, no more confusion between tools. Just a clean interface to keep your project metadata in sync.

---

## 🚀 Features

- `metapkg init`: Create a minimal `pyproject.toml` from scratch
- `metapkg add <package>`: Add dependencies directly to `pyproject.toml`
- `metapkg remove <package>`: Remove unwanted dependencies
- `metapkg scan`: Analyze `.py` files to detect used imports and suggest dependencies
- `metapkg reqs`: Generate or update `requirements.txt` from TOML
- `metapkg sync`: Sync installed packages with your TOML file (optional)
- `metapkg check`: Ensure all required fields are present for PyPI publish readiness

---

## 🔧 Installation

Install via pip:

```bash
pip install metapkg