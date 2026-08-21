# ⚡ Flowmodoro CLI & Deep Work Tracker

> A minimalist, terminal-native focus tracker designed for **uninterrupted deep work**. Built around the **Flowmodoro technique** (earned recovery based on actual flow duration).

---

## Video Demonstration

https://github.com/user-attachments/assets/0d80463e-3598-4d5c-b50a-a77a2cefddd0

---

## 📖 Table of Contents

- [What is Flowmodoro?](#-what-is-flowmodoro)
- [Installation](#-installation)
- [Quick Start (Minimalist Core)](#-quick-start-minimalist-core)
- [Basic Command Reference](#-basic-command-reference)
- [⚙️ Advanced Options & Settings](#%EF%B8%8F-advanced-options--settings)
  - [Daily Focus Goals & Break Limits](#-daily-focus-goals--break-limits)
  - [Analytics & Activity Heatmap](#-analytics--activity-heatmap)
  - [Audio & Per-Cue Repeat Controls](#-audio--per-cue-repeat-controls)
  - [Vault & Persistent Storage](#-vault--persistent-storage)
  - [Session Pruning & History](#-session-pruning--history)
  - [Data Export (CSV & JSON)](#-data-export-csv--json)
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

## 📦 Installation

### macOS & Linux (via `pipx`)

```bash
# 1. Install pipx (if not installed)
brew install pipx
pipx ensurepath

# 2. Clone and install in editable mode
git clone https://github.com/yourusername/flowmodoro-cli.git
cd flowmodoro-cli
pipx install --editable .
```

### Windows

```powershell
git clone https://github.com/yourusername/flowmodoro-cli.git
cd flowmodoro-cli
pip install -e .
```

---

## 🚀 Quick Start (Minimalist Core)

Keep it simple. You don't need any complex setup or flags to start tracking:

1. **Start an interactive focus session:**
   ```bash
   flowmodoro
   ```
2. **Set a Task & Focus:**
   - Enter your focus task/topic (or press Enter for `'Deep Work'`).
   - Work uninterrupted. Press **`Ctrl + C`** when your flow breaks.
   - Earned rest is calculated automatically. Press **`Y`** to start the rest countdown.
3. **Dismiss the Alarm:**
   - When break reaches `00:00`, a chime rings and a desktop notification appears.
   - Press **`[Enter]`** to start your next session.

---

## 💻 Basic Command Reference

For everyday minimalist usage, you only need these three core commands:

```bash
# 1. Start a default focus session
flowmodoro

# 2. Start a session directly with a specific task name
flowmodoro -t "Distributed Systems"

# 3. View your 28-day consistency heatmap & daily summary
flowmodoro -s
```

---

## ⚙️ Advanced Options & Settings

For power users who want custom audio files, vault integration, break capping, or history pruning:

### 🎯 Daily Focus Goals & Break Limits

```bash
# Set daily focus target to 4 hours (default: 6h)
flowmodoro --goal 4

# Cap breaks at 20 minutes max (prevents 40-minute breaks after 3h sessions)
flowmodoro --max-break 20

# Disable break capping (unlimited earned rest)
flowmodoro --max-break 0
```

### 📊 Analytics & Activity Heatmap

```bash
# General overview with 28-day heatmap & top topics
flowmodoro --stats

# Filter metrics for a specific topic only
flowmodoro --stats -t "Algorithms"
```

```text
==============================================================
               ⚡ FLOWMODORO ANALYTICS DASHBOARD ⚡
==============================================================

📅 Today (2026-08-21):
  • Focus Logged : 04h 15m 30s
  • Daily Goal   : [██████████████░░░░░░] 71% (04:15:30 / 06:00:00)

🗓️  28-Day Consistency Heatmap (Goal: 6h/day):
  ░░▒▓  ▓██▒  █▓██  ████  (Today)
  [· 0h  ░ <35%  ▒ <70%  ▓ <100%  █ Goal Met]

📈 Last 7 Days Activity:
  Date       | Focus Time  | Daily Target
  -----------+-------------+-----------------------------
  2026-08-15 | 05:45:10    | [████████████] 96%
  2026-08-16 | 06:00:00    | [████████████] 100%
  2026-08-17 | 04:30:00    | [█████████░░░] 75%
  2026-08-18 | 06:15:00    | [████████████] 100%
  2026-08-19 | 05:20:45    | [██████████░░] 89%
  2026-08-20 | 06:00:00    | [████████████] 100%
  2026-08-21 | 04:15:30    | [████████░░░░] 71% (Today)

🏆 Summary Highlights:
  • Daily Target    : 6 hour(s)/day
  • Total Focus     : 38h 06m 25s across 28 cycle(s)
  • Current Streak  : 7 day(s)
  • Active Vault    : /Users/YourName/Documents/ObsidianVault/flowmodoro_log.md
==============================================================
```

### 🔔 Audio & Per-Cue Repeat Controls

Customize sound cues and control whether sounds play once or loop continuously:

```bash
# 1. Interactive browser to preview & select built-in OS sounds
flowmodoro --sounds

# 2. Set custom audio files (.mp3, .wav, .m4a)
flowmodoro --sound-focus ~/Music/focus_start.wav
flowmodoro --sound-start ~/Music/break_chime.wav
flowmodoro --sound-stop ~/Music/alarm_chime.mp3

# 3. Toggle repeat loops per audio cue individually (on / off)
flowmodoro --repeat-focus off    # Focus Start: single chime (default)
flowmodoro --repeat-start off    # Break Start: single chime (default)
flowmodoro --repeat-stop off     # Break End Alarm: single chime (or 'on' for looping)

# 4. Reset all audio alerts back to OS system defaults
flowmodoro --sound-default
```

### 📂 Vault & Persistent Storage

Every session is automatically logged to `flowmodoro_data.jsonl` and auto-synced to a formatted Markdown journal (`flowmodoro_log.md`).

```bash
# View active storage paths, audio settings, and goal settings
flowmodoro --where

# Point persistent log directory to an Obsidian or Logseq vault
flowmodoro --path ~/Documents/ObsidianVault/Flowmodoro
```

### 🗑️ Session Pruning & History

```bash
# Undo / remove the most recent session
flowmodoro --undo

# Interactively browse and delete specific logs
flowmodoro --delete
```

### 💾 Data Export & Excel Visualization

Flowmodoro can generate **native Microsoft Excel workbooks (`.xlsx`) pre-loaded with interactive charts**:

```bash
# 1. Export native Excel workbook with 4 pre-built charts (.xlsx)
flowmodoro --export ~/Desktop/focus_dashboard.xlsx

# 2. Export raw CSV data table (.csv)
flowmodoro --export ~/Desktop/focus_history.csv

# 3. Export JSON format for custom scripts (.json)
flowmodoro --export ~/Desktop/focus_history.json
```


#### Recommended Excel Charts & Setup:

1. **🍩 Donut / Pie Chart (Task Allocation Share)**
   - **Pivot Table**: Rows = `task`, Values = `Sum of focus_hours`.
   - **Chart**: Insert Donut Chart $\rightarrow$ Shows percentage share of deep work per subject.

2. **📊 Clustered Column Chart (Daily Target Progress)**
   - **Pivot Table**: Rows = `date`, Values = `Sum of focus_hours`.
   - **Chart**: Insert Clustered Column Chart $\rightarrow$ Compares daily focus hours against your 6-hour goal.

3. **📈 Line Trend Chart (Session Flow Endurance)**
   - **Data**: X-Axis = `date` / `start_time`, Y-Axis = `focus_minutes`.
   - **Chart**: Insert Line Chart with Markers $\rightarrow$ Tracks whether your continuous flow duration increases over time.

4. **📑 Stacked Bar Chart (Work vs Rest Efficiency)**
   - **Pivot Table**: Rows = `date`, Values = `Sum of focus_minutes` and `Sum of break_minutes`.
   - **Chart**: Insert Stacked Bar Chart $\rightarrow$ Visualizes the $1:5$ ratio efficiency between deep work and earned recovery.



---

## 🏗️ Project Architecture

```text
flowmodoro-cli/
├── pyproject.toml              # Build metadata & entry-point definition
├── LICENSE                     # The Unlicense (Public Domain)
├── README.md                   # Complete documentation
├── .gitignore                  # Ignores local data & build artifacts
└── flowmodoro/
    ├── __init__.py             # Package initializer
    ├── cli.py                  # CLI argument parser & help menu
    ├── config.py               # Persistent config (~/.flowmodoro_config.json)
    ├── audio.py                # Sound player, preview browser & desktop banners
    ├── storage.py              # JSONL storage, Markdown sync & CSV/JSON exports
    ├── dashboard.py            # Heatmaps, task filters & ASCII progress charts
    └── timers.py               # Stopwatch flow loop & capped break countdowns
```

---

## 📄 License

This is free and unencumbered software released into the public domain ([The Unlicense](LICENSE)).

