# metapkg – Simplify Python Project Metadata Management

**metapkg** is a fast, intuitive CLI tool designed to streamline Python project metadata management. It simplifies creating, updating, and maintaining `pyproject.toml`, managing dependencies, and preparing your project for PyPI publishing.

Whether you're starting a new project or maintaining an existing one, **metapkg** keeps your metadata organized and your workflow efficient.

---

## 🚀 Features

- **Initialize Projects**: Create a `pyproject.toml` file with `metapkg init`.
- **Manage Dependencies**: Add or remove dependencies with `metapkg add` and `metapkg remove`.
- **Scan Imports**: Detect missing dependencies in your code with `metapkg scan`.
- **Generate Requirements**: Auto-generate `requirements.txt` with `metapkg reqs`.
- **Sync Environment**: Install dependencies from `pyproject.toml` with `metapkg sync`.
- **Check PyPI Readiness**: Validate `pyproject.toml` for publishing with `metapkg check`.

---

## 🔧 Installation

**metapkg** requires **Python 3.12 or higher**. It is recommended to use a virtual environment.

### Install via PyPI

```bash
pip install metapkg
````

### Install from Source

```bash
git clone https://github.com/yourusername/metapkg.git
cd metapkg
python -m pip install -e .
```

### Verify Installation

```bash
metapkg --help
```

---

## 📋 Usage

Run `metapkg --help` to see all available commands.

### Initialize a New Project

```bash
metapkg init
```

**Example Interaction**:

```
/path/to/project/pyproject.toml already exists. Overwrite? [y/N]: y  
Project name [my-project]: my-project  
Version [0.1.0]:  
Description []: My Python project  
Author []: Jane Doe  
License [MIT]:  
Minimum Python version (e.g., >=3.8, ==3.12) [>=3.8]: >=3.12  
Build backend (setuptools, hatchling, flit) [setuptools]:  
Writing to /path/to/project/pyproject.toml  
Successfully created /path/to/project/pyproject.toml  
```

---

### Add a Dependency

```bash
metapkg add requests>=2.28.1
```

**Output**:

```
Checking for pyproject.toml at /path/to/project/pyproject.toml  
Writing to /path/to/project/pyproject.toml  
Added requests>=2.28.1 to pyproject.toml  
```

---

### Remove a Dependency

```bash
metapkg remove requests
```

**Output**:

```
Checking for pyproject.toml at /path/to/project/pyproject.toml  
Writing to /path/to/project/pyproject.toml  
Removed requests from pyproject.toml  
```

---

### Scan Code for Imports

```bash
echo 'import pandas' > analysis.py
metapkg scan
```

**Output**:

```
Checking for pyproject.toml at /path/to/project/pyproject.toml  
Missing dependencies detected:  
- pandas  
Add missing dependencies to pyproject.toml? [y/N]: y  
Writing to /path/to/project/pyproject.toml  
Updated /path/to/project/pyproject.toml with missing dependencies.  
```

---

### Generate requirements.txt

```bash
metapkg reqs
```

**Output**:

```
Checking for pyproject.toml at /path/to/project/pyproject.toml  
Generated requirements.txt  
```

**Generated requirements.txt**:

```
requests>=2.28.1
pandas>=2.0.0
```

---

### Sync Dependencies

```bash
metapkg sync
```

**Output**:

```
Checking for pyproject.toml at /path/to/project/pyproject.toml  
Successfully installed missing dependencies.  
```

---

### Check PyPI Readiness

```bash
metapkg check
```

**Output**:

```
Checking for pyproject.toml at /path/to/project/pyproject.toml  
pyproject.toml is ready for PyPI publishing!  
```

If issues are found:

```
Warnings found in pyproject.toml:  
- Missing recommended field: classifiers (useful for PyPI categorization)  
```

---

## 🛠️ Example Workflow

Set up a new Python project with **metapkg**:

```bash
mkdir my-project
cd my-project
python -m venv venv
source venv/bin/activate
pip install metapkg
metapkg init
metapkg add flask>=2.0.0
echo 'import pandas' > app.py
metapkg scan
metapkg sync
metapkg reqs
metapkg check
```

This will:

* Create a project
* Add `flask`
* Detect `pandas`
* Install dependencies
* Generate `requirements.txt`
* Verify PyPI readiness

---

## 🤝 Contributing

We welcome contributions! To get started:

1. **Fork the repository**: [github.com/yourusername/metapkg](https://github.com/yourusername/metapkg)
2. **Create a branch**:

   ```bash
   git checkout -b feature/your-feature
   ```
3. **Commit changes**:

   ```bash
   git commit -m "Add your feature"
   ```
4. **Push to your fork**:

   ```bash
   git push origin feature/your-feature
   ```
5. **Open a pull request**

See our `CONTRIBUTING.md` for more details.

---

## 📬 Feedback & Issues

Found a bug or have a feature request? Open an issue on GitHub:
[github.com/yourusername/metapkg/issues](https://github.com/yourusername/metapkg/issues)

Please use the issue templates to provide clear and actionable reports.

---

## 📝 License

**metapkg** is licensed under the **MIT License**.

---

> Let’s make Python project management simpler, together!
