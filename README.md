# ⚡ Flowmodoro CLI & Deep Work Tracker

> A minimalist, terminal-based focus tracker designed for **uninterrupted deep work**. Built around the **Flowmodoro technique** (earned recovery based on actual flow duration), featuring persistent directory configuration, dual JSONL/Markdown sync, continuous alarm loops, and interactive terminal analytics.

---

## 📖 Table of Contents

- [What is Flowmodoro?](#-what-is-flowmodoro)
- [Key Features](#-key-features)
- [Requirements](#-requirements)
- [Quick Start](#-quick-start)
- [CLI Reference](#-cli-reference)
- [Persistent Storage & Path Configuration](#-persistent-storage--path-configuration)
- [Markdown Sync & Analytics](#-markdown-sync--analytics)
- [6-Hour Deep Work Protocol](#-6-hour-deep-work-protocol)
- [Cross-Platform Audio Architecture](#-cross-platform-audio-architecture)

---

## 🧠 What is Flowmodoro?

Standard Pomodoro locks you into arbitrary 25-minute intervals, often forcing breaks right when you reach peak cognitive flow. 

**Flowmodoro flips the equation:**
1. **Count-Up Timer:** Work with zero interruptions until your focus naturally breaks.
2. **Earned Recovery:** Your break time is calculated dynamically using a fixed ratio ($20\%$ or $1:5$).
   $$\text{Break Time} = \text{Focus Duration} \times 0.20$$
3. **Examples:**
   - $50\text{ min}$ Focus $\rightarrow 10\text{ min}$ Earned Break
   - $75\text{ min}$ Focus $\rightarrow 15\text{ min}$ Earned Break
   - $90\text{ min}$ Focus $\rightarrow 18\text{ min}$ Earned Break

---

## ✨ Key Features

- **Persistent Folder Configuration:** Set your custom storage folder once (e.g., an Obsidian vault); the CLI remembers it forever across sessions and system restarts until changed.
- **Dynamic Stopwatch:** Zero countdown pressure during focus; measure true deep work blocks.
- **Continuous Alarm Cue:** Sounds a repeating audio alert at the end of breaks until manually dismissed with `[Enter]`.
- **Zero External Dependencies:** Runs on standard Python 3 libraries (`ctypes`, `subprocess`, `threading`, `json`, `argparse`).
- **Dual-Layer Persistence:**
  - `flowmodoro_data.jsonl`: Machine-readable, append-only raw data.
  - `flowmodoro_log.md`: Human-readable summary table and journal compatible with Obsidian and VS Code.
- **Terminal Analytics Dashboard:** Visual ASCII progress bars tracking your daily 6-hour goal, 7-day breakdown, and active streaks.
- **Session Management:** Built-in `--undo` and interactive `--delete` tools to prune misfires.

---

## 📦 Requirements

- **Python 3.8+** (Standard installation; no `pip install` required)

---

## 🚀 Quick Start

1. **Start a Deep Work Session:**
   ```bash
   python flowmodoro.py
   ```
2. **Set a Task & Focus:**
   - Enter your focus task/topic (e.g., `Distributed Systems`, `Math Proofs`, `Paper Draft`).
   - Work uninterrupted.
   - When your flow breaks or you need a pause, press **`Ctrl + C`**.
   - Your earned rest is calculated automatically. Press **`Y`** to begin the rest countdown.

---

## 💻 CLI Reference

| Command | Short | Description |
| :--- | :--- | :--- |
| `python flowmodoro.py` | | Start an interactive focus session |
| `python flowmodoro.py --task "Task Name"` | `-t` | Start directly with a pre-set task name |
| `python flowmodoro.py --path "/target/folder"` | `-p` | **Permanently** set the storage directory for data and Markdown logs |
| `python flowmodoro.py --where` | `-w` | Inspect the currently active storage path and file locations |
| `python flowmodoro.py --stats` | `-s` | View the analytics dashboard & 7-day progress |
| `python flowmodoro.py --undo` | `-u` | Quickly delete the most recent session |
| `python flowmodoro.py --delete` | `-d` | Open interactive menu to pick and delete specific sessions |

---

## 📂 Persistent Storage & Path Configuration

Flowmodoro stores your preferred storage directory in a lightweight `flowmodoro_config.json` file beside the script.

### Setting Your Path Permanently

Run the `--path` command **once**:

```bash
# Windows (Obsidian Vault Example)
python flowmodoro.py --path "C:\Users\YourName\Documents\ObsidianVault"

# macOS / Linux
python flowmodoro.py --path "~/Documents/ObsidianVault"
```

*Output:*
```text
✓ Successfully set persistent log path to:
  📂 /Users/YourName/Documents/ObsidianVault
  All future sessions and markdown logs will save here until changed.
```

### Checking Your Active Path

```bash
python flowmodoro.py --where
```

*Output:*
```text
📂 Active Storage Directory: /Users/YourName/Documents/ObsidianVault
📄 Markdown Journal       : /Users/YourName/Documents/ObsidianVault/flowmodoro_log.md
💾 JSONL Data Store       : /Users/YourName/Documents/ObsidianVault/flowmodoro_data.jsonl
```

---

## 📊 Analytics Dashboard (`--stats`)

Run `python flowmodoro.py --stats` anytime to inspect your focus velocity:

```text
============================================================
             ⚡ FLOWMODORO ANALYTICS DASHBOARD ⚡
============================================================

📅 Today (2026-08-21):
  • Focus Logged : 04h 15m 30s
  • Daily 6h Goal: [██████████████░░░░░░] 71% (04:15:30 / 06:00:00)

📈 Last 7 Days Activity:
  Date       | Focus Time  | Daily 6h Target
  -----------+-------------+-----------------------------
  2026-08-15 | 05:45:10    | [████████████] 96%
  2026-08-16 | 06:00:00    | [████████████] 100%
  2026-08-17 | 04:30:00    | [█████████░░░] 75%
  2026-08-18 | 06:15:00    | [████████████] 100%
  2026-08-19 | 05:20:45    | [██████████░░] 89%
  2026-08-20 | 06:00:00    | [████████████] 100%
  2026-08-21 | 04:15:30    | [████████░░░░] 71% (Today)

🏆 Summary Highlights:
  • Total Sessions  : 28
  • Lifetime Focus  : 38h 06m 25s
  • Current Streak  : 7 day(s)
  • Active Directory: /Users/YourName/Documents/ObsidianVault
  • Markdown Vault  : /Users/YourName/Documents/ObsidianVault/flowmodoro_log.md
============================================================
```

---

## 📝 Markdown Output Format (`flowmodoro_log.md`)

Every completed or removed session updates the generated Markdown journal automatically:

```markdown
# ⚡ Flowmodoro Deep Work Journal

> *Last updated: 2026-08-21 11:45:00*

## 📊 Overview Metrics

| Metric | Value |
| :--- | :--- |
| **Today's Focus** | `04h 15m 30s` (3 sessions) |
| **All-Time Focus** | `38h 06m 25s` |
| **Total Rest Earned** | `07h 37m 17s` |
| **Total Completed Cycles** | `28` |
| **Active Days** | `7` |

## 📝 Session Logs

| Date | Task / Topic | Start | End | Focus | Earned Break |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 2026-08-21 | Algorithms & Data Structures | 09:30:10 | 11:05:40 | `01:35:30` | `19:06` |
| 2026-08-21 | Research & Synthesis | 07:45:00 | 09:10:00 | `01:25:00` | `17:00` |
| 2026-08-21 | Core Math Proofs | 06:00:00 | 07:15:00 | `01:15:00` | `15:00` |
```

---

## 🏛️ The 6:00 AM – 12:00 PM Deep Work Protocol

To execute 6 daily hours of deep work sustainably:

1. **6:00 AM – 8:30 AM (Peak Analytical Block):** Tackle the primary theoretical bottleneck. Zero communication, notifications, or tab-switching.
2. **8:30 AM – 8:50 AM (Physical Reset):** Hydrate, walk outside, stretch. Strictly no feeds or screens.
3. **8:50 AM – 10:30 AM (Deep Execution Block):** Problem sets, coding, or rigorous writing.
4. **10:30 AM – 10:50 AM (Rest / Fuel):** Screen-free rest and recovery.
5. **10:50 AM – 12:00 PM (Review & Synthesis):** Spaced repetition, notes integration, and organizing tomorrow's priorities.

---

## 🛠️ Cross-Platform Audio Architecture

| Platform | Audio Mechanism | Behavior |
| :--- | :--- | :--- |
| **Windows** | `ctypes.windll.kernel32.Beep` / PowerShell | Direct hardware tone ($1000\text{ Hz}, 350\text{ ms}$) [cite: 4] |
| **macOS** | `afplay /System/Library/Sounds/Glass.aiff` | Native macOS audio playback [cite: 4] |
| **Linux** | `paplay` / `aplay` | PulseAudio / ALSA sound player [cite: 4] |
| **WSL** | Routed to `powershell.exe` | Seamless alert pass-through to host OS [cite: 4] |
