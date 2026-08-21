# ⚡ Flowmodoro CLI & Deep Work Tracker

> A minimalist, terminal-native focus tracker designed for **uninterrupted deep work**. Built around the **Flowmodoro technique** (earned recovery based on actual flow duration), featuring desktop banner notifications, 28-day activity heatmaps, CSV/JSON exports, and customizable daily goals.

---

## 📖 Table of Contents

- [What is Flowmodoro?](#-what-is-flowmodoro)
- [Key Features](#-key-features)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [CLI Command Reference](#-cli-command-reference)
- [Daily Focus Goals & Break Limits](#-daily-focus-goals--break-limits)
- [Analytics & Activity Heatmap](#-analytics--activity-heatmap)
- [Data Export (CSV & JSON)](#-data-export-csv--json)
- [Audio & Alarm System](#-audio--alarm-system)
- [Persistent Storage & Markdown Sync](#-persistent-storage--markdown-sync)
- [Session Management & Pruning](#-session-management--pruning)
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

- **Desktop Banner Notifications:** Native notifications via `osascript` (macOS), `notify-send` (Linux), and PowerShell (Windows).
- **28-Day Consistency Heatmap:** Terminal GitHub-style contribution graph (`░ ▒ ▓ █`) tracking daily habit momentum.
- **Task & Tag Analytics:** Filter focus metrics by specific subjects (`flowmodoro --stats -t "Math"`).
- **Configurable Break Cap (`--max-break`):** Limit maximum rest to prevent long flow sessions from derailing momentum.
- **CSV & JSON Data Export (`--export`):** One-click exports to import into Excel, Notion, or Google Sheets.
- **Customizable Daily Goals (`--goal`):** Configurable target (e.g. 4h, 6h, 8h/day).
- **Global Terminal Access:** Run `flowmodoro` from any directory.
- **Zero External Dependencies:** Built purely with Python 3 standard libraries.

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

## 🚀 Quick Start

1. **Start an interactive focus session:**
   ```bash
   flowmodoro
   ```
2. **Set a Task & Focus:**
   - Enter your focus task/topic (e.g., `Distributed Systems`, `Linear Algebra`).
   - Work uninterrupted. Press **`Ctrl + C`** when your flow breaks.
   - Earned rest is calculated automatically. Press **`Y`** to begin the countdown.
3. **Dismiss the Alarm:**
   - When the break reaches `00:00`, the terminal chime rings and a desktop banner appears.
   - Press **`[Enter]`** to dismiss the alarm.

---

## 💻 CLI Command Reference

```text
======================================================================
                 ⚡ FLOWMODORO CLI HELP & COMMANDS ⚡
======================================================================

USAGE:
  flowmodoro [OPTIONS]

CORE COMMANDS:
  flowmodoro                     Start an interactive focus & flow session
  flowmodoro -t, --task <NAME>   Start session directly with designated task name
  flowmodoro -s, --stats         Display analytics dashboard & 28-day heatmap
  flowmodoro -s -t <TOPIC>       Display analytics filtered by a specific task/tag

GOALS, LIMITS & STORAGE:
  flowmodoro -g, --goal <HOURS>  Set daily focus goal in hours (default: 6h)
  flowmodoro --max-break <MINS>  Cap maximum break duration (e.g. 20; 0 to uncap)
  flowmodoro -p, --path <DIR>    Set persistent folder for Markdown & JSONL data
  flowmodoro -w, --where         Show current storage paths, audio settings & goal
  flowmodoro -e, --export <FILE> Export session logs to CSV or JSON format

AUDIO CONFIGURATION:
  flowmodoro --sounds            Interactive browser to preview & select OS native sounds
  flowmodoro --sound-start <F>   Set custom audio for break start (.mp3, .m4a, .wav)
  flowmodoro --sound-stop <F>    Set custom audio for break completion alarm
  flowmodoro --sound-default     Reset all sound cues back to OS system defaults

SESSION PRUNING & HISTORY:
  flowmodoro -u, --undo          Remove the most recently recorded session
  flowmodoro -d, --delete        Interactively browse and delete specific logs

HELP:
  flowmodoro -h, --help          Show this command reference
======================================================================
```

---

## 🎯 Daily Focus Goals & Break Limits

```bash
# Set daily target to 4 hours
flowmodoro --goal 4

# Cap breaks at 20 minutes max (prevents 40-minute breaks after 3h sessions)
flowmodoro --max-break 20

# Disable break capping (unlimited earned rest)
flowmodoro --max-break 0
```

---

## 📊 Analytics & Activity Heatmap

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

🏷️  Top Focus Objectives:
  • Distributed Systems    : 18h 40m 10s  (49%)
  • Math Proofs            : 12h 10m 00s  (32%)
  • Paper Drafting         : 07h 16m 15s  (19%)

🏆 Summary Highlights:
  • Daily Target    : 6 hour(s)/day
  • Total Focus     : 38h 06m 25s across 28 cycle(s)
  • Current Streak  : 7 day(s)
  • Active Vault    : /Users/YourName/Documents/ObsidianVault/flowmodoro_log.md
==============================================================
```

---

## 💾 Data Export (CSV & JSON)

Export your logs to analyze in Notion, Google Sheets, or Excel:

```bash
# Export to CSV
flowmodoro --export ~/Documents/focus_history.csv

# Export to JSON
flowmodoro --export ~/Documents/focus_history.json
```

---

## 🔔 Audio & Alarm System

Customize audio cues for break starts and break completion alarms:

```bash
# Open interactive sound browser to preview & select OS native sounds
flowmodoro --sounds

# Set custom audio files (.mp3, .wav, .m4a)
flowmodoro --sound-start ~/Music/break_chime.wav
flowmodoro --sound-stop ~/Music/alarm_chime.mp3

# Reset all audio alerts back to OS system defaults
flowmodoro --sound-default
```

---

## 📂 Persistent Storage & Markdown Sync

Every session is automatically logged to two formats:
1. **`flowmodoro_data.jsonl`**: Raw JSON Lines data store for analytics and exports.
2. **`flowmodoro_log.md`**: Beautifully formatted Markdown journal with summary metrics and table logs (perfect for Obsidian, Logseq, or PKM vaults).

```bash
# View active storage paths, audio settings, and goal settings
flowmodoro --where

# Change persistent log directory (e.g. point to an Obsidian vault)
flowmodoro --path ~/Documents/ObsidianVault/Flowmodoro
```

---

## 🗑️ Session Management & Pruning

Accidentally recorded a session or need to remove an outlier?

```bash
# Undo / remove the most recent session
flowmodoro --undo

# Interactively browse and select specific sessions to delete
flowmodoro --delete
```

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
