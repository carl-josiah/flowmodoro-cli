# ⚡ Flowmodoro CLI & Deep Work Tracker

> A minimalist, terminal-native focus tracker designed for **uninterrupted deep work**. Built around the **Flowmodoro technique** (earned recovery based on actual flow duration), featuring global command-line access, interactive native system sound selection, persistent Obsidian/Markdown sync, continuous alarms, and terminal analytics.

---

## 📖 Table of Contents

- [What is Flowmodoro?](#-what-is-flowmodoro)
- [Key Features](#-key-features)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [CLI Command Reference](#-cli-command-reference)
- [Audio & Alarm System](#-audio--alarm-system)
- [Persistent Storage & Markdown Vault Sync](#-persistent-storage--markdown-vault-sync)
- [Terminal Analytics Dashboard](#-terminal-analytics-dashboard)
- [6-Hour Deep Work Protocol](#-6-hour-deep-work-protocol)
- [Project Architecture](#-project-architecture)

---

## 🧠 What is Flowmodoro?

Standard Pomodoro forces artificial 25-minute cutoffs that disrupt deep cognitive flow states. 

**Flowmodoro flips the equation:**
1. **Count-Up Stopwatch:** Work without arbitrary timers until your focus naturally breaks.
2. **Earned Recovery:** Break duration is calculated dynamically using a fixed ratio ($20\%$ or $1:5$).
   $$\text{Break Time} = \text{Focus Duration} \times 0.20$$
3. **Pacing Examples:**
   - $50\text{ min}$ Focus $\rightarrow 10\text{ min}$ Earned Break
   - $75\text{ min}$ Focus $\rightarrow 15\text{ min}$ Earned Break
   - $90\text{ min}$ Focus $\rightarrow 18\text{ min}$ Earned Break

---

## ✨ Key Features

- **Global CLI Command:** Run `flowmodoro` directly from any terminal directory.
- **Native System Sound Browser (`--sounds`):** Discover, preview, and select built-in macOS, Windows, and Linux audio chimes.
- **Custom Audio Support:** Use your own `.mp3`, `.m4a`, `.wav`, or `.aiff` files for focus-stop and break-complete alarms.
- **Continuous Alarm Loop:** Plays your alarm repeatedly at the end of breaks until manually dismissed with `[Enter]`.
- **Persistent Storage Configuration:** Set your custom storage folder once (e.g., an Obsidian vault); the CLI remembers it forever.
- **Dual-Layer Persistence:**
  - `flowmodoro_data.jsonl`: Machine-readable, append-only raw data.
  - `flowmodoro_log.md`: Human-readable summary table and journal formatted for Obsidian and VS Code.
- **Terminal Analytics Dashboard (`--stats`):** Visual ASCII progress bars tracking your daily 6-hour target, 7-day breakdown, and active streaks.
- **Session Management:** Built-in `--undo` and interactive `--delete` tools to prune accidental runs.
- **Zero External Dependencies:** Built entirely with Python 3 standard libraries.

---

## 📦 Installation

### macOS & Linux (Recommended via `pipx`)

Install [pipx](https://pypa.github.io/pipx/) if not already installed, then install Flowmodoro in editable mode:

```bash
# 1. Install pipx (if needed)
brew install pipx
pipx ensurepath

# 2. Clone and install locally
git clone [https://github.com/yourusername/flowmodoro-cli.git](https://github.com/yourusername/flowmodoro-cli.git)
cd flowmodoro-cli
pipx install --editable .
