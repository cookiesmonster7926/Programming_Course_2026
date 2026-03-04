# Week 2 (03/06) - Basic Programming Lab

**English** | [繁體中文](README_zh-TW.md)

## 📝 Implementation Steps

### Step 1: Installation and Environment Check
* **What to do**: Install the modern Python package manager `uv` according to your operating system.
* **What to expect**: After typing `uv --version` in your Terminal / PowerShell, the version number (e.g., `uv 0.10.7`) must successfully appear.

### Step 2: Initialize Project Folder
* **What to do**: Use `uv` to initialize a brand new project and specify the Python version (recommend using `3.11`).
* **What to expect**:
  * `pyproject.toml` (configuration file) is automatically generated in the project folder.
  * `main.py` (program entry point) is automatically generated in the project folder.

### Step 3: Code Migration and Package Management
* **What to do**:
  * Migrate the content of the "Typing Challenge" from last semester into `main.py`.
  * Use `uv` to install third-party packages required for the project (such as `matplotlib`, etc.).
* **What to expect**:
  * `uv.lock` file: This is the "Environment DNA" of the project, ensuring consistency across different computers.
  * Complete program: Includes the question display, countdown timer (using `after`), and the final score screen.

### Step 4: Create Project Virtual Environment
* **What to do**: Create and activate a virtual environment specifically for this project inside the project directory.
* **What to expect**:
  * A hidden folder `.venv/` appears in the directory.
  * Environment successfully activated: Your terminal prompt should show the project name in parentheses, for example `(typing_game)`.

### Step 5: Upload to GitHub
* **What to do**: Push the entire project to a public repository on GitHub.
* **What to expect**:
  * The project on GitHub must contain: `pyproject.toml`, `uv.lock`, `main.py`, `.gitignore`, `README.md`.
  * ❌ **IMPORTANT**: Ensure the `.venv` folder is excluded using `.gitignore`. Only upload configuration files and source code.

---

## 🎮 Exercise 1: SPEED TYPING CHALLENGE

You need to build a "Typing Game" by yourself.

### 🎯 Mandatory Objectives (All are required, otherwise the task is considered failed!)
- [ ] Tkinter GUI display (Cannot just use the terminal)
- [ ] Countdown timer functionality
- [ ] Number of rounds input functionality
- [ ] Correct / Incorrect feedback prompts
- [ ] Implement at least one difficulty level
- [ ] Final score summary screen
- [ ] Question display area & Input box
- [ ] Real-time color feedback (Changing color character by character)
- [ ] Display typing speed (WPM)
- [ ] Animation effects (UI Optimization)
- [ ] Multi-difficulty system (e.g., NORMAL, HARD, NIGHTMARE)
- [ ] Custom question bank

### 📊 Difficulty Level Reference:
* **NORMAL**: Displays a single English word (Time limit: 10 seconds/question)
* **HARD**: Displays a phrase with two words (Time limit: 10 seconds/question)
* **NIGHTMARE**: Displays a full English sentence (Time limit: 15 seconds/question)

---

## ✅ Self-Verification Stage
Simulate running on another device:
1. **Switch directory**: Find a completely different folder on your computer (e.g., switch from Desktop to Downloads).
2. **Re-clone the project**: `git clone` your own GitHub repository.
3. **Rebuild and sync environment**: Enter the folder and run `uv sync` (this will automatically rebuild the environment based on `uv.lock`).
4. **Run test**: Execute `uv run main.py`

🎉 **Success Criteria**: The program should launch successfully without needing to manually install any Python version or packages!

---

## 📤 Submission Guidelines

**Submission Deadline:** March 6, 2026 | 3:30 PM

Please upload the class notes file and GPT chat PDF to the Week 2 submission area. The submission must include:
1. **Notes File (PDF)**: Containing the code for each Step and screenshots of the execution results.
2. **GPT Chat Content (PDF)**
3. **GitHub Project URL (Public)**
4. **Entire Project Folder** (Must include: `README.md`, `main.py`, `pyproject.toml`, `uv.lock`, `.gitignore`)

⚠️ *Please compress all required files into a single `.zip` file before uploading to iLearn.*
