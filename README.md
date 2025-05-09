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
```

Or install from source:

```bash
git clone https://github.com/yourusername/metapkg.git
cd metapkg
python -m pip install -e .
```

---

## 📋 Example Usage

```bash
metapkg init
metapkg add flask requests
metapkg scan
metapkg reqs
```

---

## 🤝 Contributing

Contributions are welcome! Please read our [contributing guide](CONTRIBUTING.md) to get started.

---

## 📬 Feedback & Issues

Have a feature request or found a bug? Open an issue on GitHub!

Let’s make managing Python projects easier, together.

---

## 🐛 2. Example Issue Template (`.github/ISSUE_TEMPLATE/feature_request.md`)

Create this in your repo under `.github/ISSUE_TEMPLATE/feature_request.md`:

```markdown
---
name: Feature Request
about: Suggest an idea for improving metapkg
title: "[Feature] "
labels: enhancement
assignees:
---

### 🌟 Feature Description

A clear and concise description of what the feature should do and why it would be useful.

### 📦 Use Case

Explain how this feature would improve the workflow or solve a problem.

### 🧩 Proposed Behavior

Describe how the feature should work in practice. Include any CLI examples if applicable.

### 🧪 Alternatives Considered

What other ways have you thought of solving this?

### ✅ Additional Context

Add any screenshots, code snippets, or links that might help clarify the request.
```

---

## 🐞 Bug Report Template (Optional)

You can also add a bug report template at `.github/ISSUE_TEMPLATE/bug_report.md`:

```markdown
---
name: Bug Report
about: Report unexpected behavior in metapkg
title: "[Bug] "
labels: bug
assignees:
---

### 🐞 Describe the Bug

A clear and concise description of what went wrong.

### 🔁 Steps to Reproduce

Steps to reproduce the behavior:

1. Run command: `...`
2. See error: `...`

### 🖥️ Expected Behavior

What did you expect to happen?

### 🧪 Actual Behavior

What actually happened?

### 📦 Environment Info

Run `metapkg --version` and paste the output here.

Also include:
- OS: Windows/macOS/Linux
- Python version
- pyproject.toml contents (if relevant)

### ✅ Additional Context

Add any logs, screenshots, or extra info that could help.
```

---

## ✅ Next Steps

Once you’ve added these, you’ll have a great foundation for users and contributors to understand and engage with your project.