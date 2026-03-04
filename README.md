# 🎓 2026 Programming Course - TA Workspace

**English** | [繁體中文](README_zh-TW.md)

![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)
![Managed with uv](https://img.shields.io/badge/managed%20with-uv-purple)

Welcome to the TA workspace for the 2026 Programming Course! This repository is your **central navigation hub**. 

Here you will find weekly example code, lab exercises, and supplementary materials provided by the Teaching Assistant. To ensure a smooth and consistent development experience across all operating systems, this project strictly uses [uv](https://astral.sh/uv) to manage Python environments and dependencies.

> [!IMPORTANT]
> **Update Notice:**
> Weekly example code and materials will be uploaded to this repository every **Sunday**. Please remember to run `git pull` regularly to sync the latest updates!

---

## 🗺️ Course Directory & Navigation

Click the folder links in the table below to access the specific code and detailed instructions for each week:

| Week | Directory / Link | Topic & Learning Objectives |
| :--- | :--- | :--- |
| **Week 02** | [📂 Week02_0306_demo](./Week02_0306_demo/) | Environment setup, basic `uv` usage, Speed Typing Challenge GUI |
| **Week 03** | 🚧 *Coming this Sunday* | - |
| **Week 04** | 🚧 *Coming later* | - |

*(This table will be continuously updated by the TA...)*

---

## 🚀 Quick Start for Students

Follow these three simple steps to run the TA's example code seamlessly on your local machine:

### Step 1: Install `uv`

If you haven't installed `uv` yet, open your Terminal or PowerShell and run the appropriate command:

* **macOS / Linux**:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

* **Windows**:
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Step 2: Clone & Sync Environment

Clone this repository to your computer, navigate into the directory, and let `uv` handle the rest:

```bash
# Clone the repository
git clone https://github.com/cookiesmonster7926/Programming_Course_2026.git

# Enter the workspace directory
cd Programming_Course_2026

# Sync the TA's exact environment
uv sync
```

> 💡 **Tip:** Running `uv sync` automatically reads the `uv.lock` file to create a pure virtual environment with the correct Python version. You **do not** need to manually run `pip install`!

### Step 3: Run the Examples

To execute a specific week's script, make sure you are in the root `Programming_Course_2026` directory, and use the `uv run` command followed by the file path. For example:

```bash
uv run Week02_0306_demo/main.py
```