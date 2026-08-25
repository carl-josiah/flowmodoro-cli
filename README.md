# ⚡ Flowmodoro CLI & Deep Work Tracker

<div align="center">

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Unlicense-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux%20%7C%20Windows-lightgrey.svg)](#-installation)
[![Code Style](https://img.shields.io/badge/code%20style-PEP%208-brightgreen.svg)](#-software-engineering--architecture)
[![Fuzz Tested](https://img.shields.io/badge/fuzzing-100%25%20passed-success.svg)](#-software-engineering--architecture)

**A minimalist, terminal-native focus tracker built for uninterrupted cognitive flow.**  
*Earned recovery based on actual deep work duration, with night owl day cutoffs, vault auto-sync, and zero-overlap audio controls.*

[Quick Start](#-quick-start-minimalist-core) • [Features](#-key-features) • [Commands](#-command-reference) • [Analytics](#-analytics--dashboard) • [Night Owl Mode](#-night-owl-day-cutoff)

---

### 🎥 Video Demonstration

https://github.com/user-attachments/assets/0d80463e-3598-4d5c-b50a-a77a2cefddd0

</div>

---

## 📖 Table of Contents

- [🧠 What is Flowmodoro?](#-what-is-flowmodoro)
- [✨ Key Features](#-key-features)
- [📦 Installation](#-installation)
- [🚀 Quick Start (Minimalist Core)](#-quick-start-minimalist-core)
- [💻 Command Reference Table](#-command-reference-table)
- [📊 Analytics & Dashboard](#-analytics--dashboard)
- [🌙 Night Owl Day Cutoff Hour](#-night-owl-day-cutoff-hour)
- [🔔 Audio & Per-Cue Controls](#-audio--per-cue-controls)
- [📂 Vault Sync & Storage Management](#-vault-sync--storage-management)
- [🗑️ History & Session Pruning](#%EF%B8%8F-history--session-pruning)
- [💾 Native Excel & Data Exports](#-native-excel--data-exports)
- [🏗️ Software Engineering & Architecture](#%EF%B8%8F-software-engineering--architecture)
- [📄 License](#-license)

---

## 🧠 What is Flowmodoro?

Standard Pomodoro timers enforce artificial 25-minute cutoffs that forcefully break deep cognitive flow states right when your brain is performing at its peak.

**Flowmodoro flips the equation:**
1. **Count-Up Stopwatch:** Work without arbitrary timers until your focus naturally breaks.
2. **Earned Recovery Ratio:** Rest duration is calculated dynamically at a fixed $1:5$ ($20\%$) ratio.
   $$\text{Earned Break} = \text{Focus Duration} \times 0.20$$
3. **Pacing Examples:**
   - $40\text{ min}$ Continuous Focus $\rightarrow 8\text{ min}$ Earned Break
   - $60\text{ min}$ Continuous Focus $\rightarrow 12\text{ min}$ Earned Break
   - $90\text{ min}$ Continuous Focus $\rightarrow 18\text{ min}$ Earned Break

---

## ✨ Key Features

- ⚡ **Stopwatch Flow Loop:** Work uninterrupted until your flow breaks. Press `Ctrl + C` to save.
- 🛑 **Strict Input Validation & Control:** Prompts strictly reject invalid entries and respond only to `[Y/n/c/q]` or `Ctrl + C`.
- 🌙 **Night Owl Day Cutoff (`--cutoff`):** Set a cutoff time (e.g., 3:00 AM) so late-night sessions automatically log under the previous day's goals and streaks.
- 🏷️ **Task & Objective Breakdown:** Analytics dashboard displays session counts, focus hours, and percentage share across all objectives.
- 🔇 **Audio Process Management:** Zero audio overlap; previous chimes or alarms are cleanly terminated before new sounds start.
- 📊 **Native Excel Chart Export:** Generates pre-formatted `.xlsx` workbooks with donut charts, column charts, and pivot tables.
- 📓 **Markdown Vault Sync:** Auto-syncs in real-time with Obsidian, Logseq, and Notion vaults (`flowmodoro_log.md`).

---

## 📦 Installation

### macOS & Linux (via `pipx` or `pip`)

```bash
# Clone the repository
git clone https://github.com/yourusername/flowmodoro-cli.git
cd flowmodoro-cli

# Install in editable mode via pipx (recommended)
pipx install --editable .

# Or install via pip
pip install -e . --break-system-packages
```

### Windows

```powershell
git clone https://github.com/yourusername/flowmodoro-cli.git
cd flowmodoro-cli
pip install -e .
```

---

## 🚀 Quick Start (Minimalist Core)

1. **Launch Flowmodoro:**
   ```bash
   flowmodoro
   ```
2. **Set Objective & Start Flow:**
   - Enter your focus task (or press Enter for `'DEEP_WORK'`).
   - Focus without arbitrary limits. Press **`Ctrl + C`** when your session ends.
3. **Flexible Break & Restart Prompts:**
   - **Earned Break Prompt:** `Start earned break now? [Y/n/c/q]` (`Y` = rest, `c`/`n` = cancel break, `q` = quit).
   - **Next Session Confirmation:** `Start another focus session on 'TASK'? [Y/n/q]`. A new timer is **never** auto-started without explicit confirmation!

---

## 💻 Command Reference Table

| Command | Option / Flag | Description | Example |
| :--- | :--- | :--- | :--- |
| **Interactive Mode** | *(none)* | Start interactive focus session loop | `flowmodoro` |
| **Direct Task** | `-t, --task <NAME>` | Start focus session immediately with task name | `flowmodoro -t "Distributed Systems"` |
| **Analytics Dashboard** | `-s, --stats` | View 28-day heatmap, task breakdown & streak summary | `flowmodoro --stats` |
| **Filter Dashboard** | `-s -t <NAME>` | View dashboard filtered for a specific task | `flowmodoro --stats -t "Algorithms"` |
| **Daily Goal** | `-g, --goal <HOURS>` | Set daily deep work target in hours (default: `4h`) | `flowmodoro --goal 5` |
| **Night Owl Cutoff** | `--cutoff <HOUR>` | Set day cutoff hour (e.g. `3` for 3:00 AM) | `flowmodoro --cutoff 3` |
| **Max Break Cap** | `--max-break <MINS>`| Cap maximum break duration (0 to uncap) | `flowmodoro --max-break 20` |
| **Storage Vault** | `-p, --path <DIR>` | Set persistent folder for Markdown & JSONL data | `flowmodoro -p ~/Vault/Flowmodoro` |
| **Show Active Config** | `-w, --where` | Display active paths, goal, cutoff & audio settings | `flowmodoro --where` |
| **Data Export** | `-e, --export <FILE>`| Export logs to `.xlsx`, `.csv`, or `.json` | `flowmodoro --export ~/Desktop/stats.xlsx` |
| **Sound Browser** | `--sounds` | Interactive browser for native system sounds | `flowmodoro --sounds` |
| **Custom Focus Sound** | `--sound-focus <FILE>`| Set custom audio file for focus start | `flowmodoro --sound-focus start.wav` |
| **Custom Break Sound** | `--sound-start <FILE>`| Set custom audio file for break start | `flowmodoro --sound-start break.mp3` |
| **Custom Alarm Sound** | `--sound-stop <FILE>` | Set custom audio file for break complete alarm | `flowmodoro --sound-stop alarm.mp3` |
| **Toggle Alarm Repeat**| `--repeat-stop <on/off>`| Enable/disable looping break alarm | `flowmodoro --repeat-stop off` |
| **Reset Audio** | `--sound-default` | Reset audio cues back to OS defaults | `flowmodoro --sound-default` |
| **Undo Session** | `-u, --undo` | Remove most recently logged session | `flowmodoro --undo` |
| **Interactive Delete** | `-d, --delete` | Mass delete sessions by range, list, or task | `flowmodoro --delete` |
| **Delete by Task** | `--delete-task <T>` | Purge all sessions matching a task name | `flowmodoro --delete-task test` |
| **Clear History** | `--clear-all` | Purge all recorded session logs | `flowmodoro --clear-all` |

---

## 📊 Analytics & Dashboard

Run `flowmodoro --stats` to inspect your deep work performance, consistency heatmaps, and objective breakdown:

```text
==============================================================
               ⚡ FLOWMODORO ANALYTICS DASHBOARD ⚡
==============================================================

📅 Today (2026-08-26):
  • Focus Logged : 04h 15m 30s
  • Daily Goal   : [████████████████████] 106% (04:15:30 / 04:00:00)

🗓️  28-Day Consistency Heatmap (Goal: 4h/day):
  ░░▒▓  ▓██▒  █▓██  ████  (Today)
  [· 0h  ░ <35%  ▒ <70%  ▓ <100%  █ Goal Met]

📈 Last 7 Days Activity:
  Date       | Focus Time  | Daily Target            | Goal Status
  -----------+-------------+-------------------------+------------
  2026-08-20 | 04:10:00    | [████████████] 100%     | ✓ Goal Met
  2026-08-21 | 05:45:10    | [████████████] 100%     | ✓ Goal Met
  2026-08-22 | 02:30:00    | [███████░░░░░] 62%      | Missed
  2026-08-23 | 04:15:00    | [████████████] 100%     | ✓ Goal Met
  2026-08-24 | 06:20:45    | [████████████] 100%     | ✓ Goal Met
  2026-08-25 | 04:00:00    | [████████████] 100%     | ✓ Goal Met
  2026-08-26 | 04:15:30    | [████████████] 106%     (Today) | ✓ Goal Met

🏷️  Task & Objective Breakdown:
  Task Name              | Sessions | Total Time  | Share
  -----------------------+----------+-------------+-------
  DISTRIBUTED_SYSTEMS    | 12       | 24h 10m 00s |   63%
  ALGORITHMS             | 8        | 09h 45m 15s |   26%
  DEEP_WORK              | 4        | 04h 11m 10s |   11%

🏆 Summary Highlights:
  • Daily Target    : 4 hour(s)/day
  • Total Focus     : 38h 06m 25s across 24 cycle(s)
  • Current Streak  : 4 day(s) (Goal-Met Days)
  • Active Vault    : /Users/YourName/Documents/ObsidianVault/flowmodoro_log.md
==============================================================
```

---

## 🌙 Night Owl Day Cutoff Hour

If you work late into the night, standard midnight cutoffs reset your focus metrics right in the middle of a session.

Set a custom **Day Cutoff Hour** (e.g. `3` for 3:00 AM):

```bash
# Set cutoff to 3:00 AM
flowmodoro --cutoff 3

# Reset cutoff back to midnight (00:00)
flowmodoro --cutoff 0
```

> **How it works:** When cutoff is set to `3`, any focus session started between 00:00 AM and 02:59 AM is automatically attributed to the previous logical date. Running `flowmodoro --stats` at 1:30 AM evaluates `2026-08-25` as Today.

---

## 🔔 Audio & Per-Cue Controls

Customize sounds and toggle loop playback per alert type:

```bash
# 1. Browse and preview native system sounds interactively
flowmodoro --sounds

# 2. Assign custom audio files (.mp3, .wav, .m4a)
flowmodoro --sound-focus ~/Music/focus_chime.wav
flowmodoro --sound-start ~/Music/break_start.mp3
flowmodoro --sound-stop ~/Music/alarm.mp3

# 3. Control per-cue repeating loops
flowmodoro --repeat-focus off    # Focus Start chime: single trigger (default)
flowmodoro --repeat-start off    # Break Start chime: single trigger (default)
flowmodoro --repeat-stop off     # Break Alarm: single trigger (or 'on' for looping)

# 4. Reset audio alerts to system defaults
flowmodoro --sound-default
```

---

## 📂 Vault Sync & Storage Management

All sessions are persisted in `flowmodoro_data.jsonl` and formatted into Markdown journals (`flowmodoro_log.md`):

```bash
# View storage paths, audio settings, cutoff hour, and goals
flowmodoro --where

# Connect storage folder to Obsidian or Logseq vault
flowmodoro --path ~/Documents/ObsidianVault/Flowmodoro
```

---

## 🗑️ History & Session Pruning

```bash
# 1. Interactive mass deletion (by range '1-5', list '1,3,5', 'all', or task name)
flowmodoro --delete

# 2. Delete all sessions for a specific topic
flowmodoro --delete-task "TEST_TASK"

# 3. Undo the most recent session
flowmodoro --undo

# 4. Clear all recorded history
flowmodoro --clear-all
```

---

## 💾 Native Excel & Data Exports

Flowmodoro exports formatted native Microsoft Excel workbooks (`.xlsx`) pre-loaded with charts:

```bash
# Export native Excel workbook with 4 pre-built charts
flowmodoro --export ~/Desktop/focus_report.xlsx

# Export raw CSV
flowmodoro --export ~/Desktop/focus_history.csv

# Export JSON data
flowmodoro --export ~/Desktop/focus_history.json
```

---

## 🏗️ Software Engineering & Architecture

Built following clean software engineering principles:
- **High Cohesion & Low Coupling:** Decoupled storage, configuration, audio process management, and timer loops.
- **Process Tracking:** Thread-safe audio management (`stop_active_audio()`) prevents overlapping audio processes.
- **100% Fuzz-Tested:** Stress-tested against malformed JSON, invalid inputs, NaN/Inf bounds, and file corruption.

```text
flowmodoro-cli/
├── pyproject.toml              # Build configuration & entry points
├── LICENSE                     # The Unlicense (Public Domain)
├── README.md                   # Complete documentation reference
└── flowmodoro/
    ├── __init__.py             # Package initializer
    ├── cli.py                  # CLI parser, command dispatcher & prompt loops
    ├── config.py               # Settings manager & logical date resolution
    ├── audio.py                # Process-tracked audio player & banner alerts
    ├── storage.py              # JSONL data store, Markdown sync & Excel exports
    ├── dashboard.py            # Analytics engine, heatmaps & task breakdown
    └── timers.py               # Flow stopwatch timer & break countdowns
```

---

## 📄 License

This software is released into the public domain under [The Unlicense](LICENSE).
