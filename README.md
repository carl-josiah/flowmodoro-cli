# ⚡ Flowmodoro CLI & Deep Work Tracker

> A minimalist, terminal-based focus tracker designed for **uninterrupted deep work**. Built around the **Flowmodoro technique** (earned recovery based on actual flow duration), with dual JSONL/Markdown persistence, continuous audio alarms, and an interactive analytics dashboard.

---

## 📖 Table of Contents

- [What is Flowmodoro?](#-what-is-flowmodoro)
- [Key Features](#-key-features)
- [Requirements](#-requirements)
- [Quick Start](#-quick-start)
- [CLI Reference](#-cli-reference)
- [Data Storage & Markdown Sync](#-data-storage--markdown-sync)
- [6-Hour Deep Work Protocol](#-6-hour-deep-work-protocol)
- [Architecture & Platform Support](#-architecture--platform-support)

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

- **Dynamic Stopwatch:** Zero countdown pressure during focus; measure true deep work blocks.
- **Continuous Alarm Cue:** Sounds a repeating audio alert at the end of breaks until manually dismissed with `[Enter]`.
- **Zero External Dependencies:** Runs on standard Python 3 libraries (`ctypes`, `subprocess`, `threading`, `json`, `argparse`).
- **Cross-Platform Audio:** Clean fallback support across macOS, Linux, Windows, and WSL.
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

1. **Clone or Download the script:**
   ```bash
   # Save flowmodoro.py to your project directory
   python flowmodoro.py
   ```

2. **Start a Deep Work Session:**
   - When prompted, enter your current focus objective (e.g., `Compiler Design`, `Math Proofs`, `Paper Draft`).
   - Focus uninterrupted.
   - When your flow breaks or you need a pause, press **`Ctrl + C`**.
   - Your earned rest is calculated automatically. Press **`Y`** to begin the rest countdown.

---

## 💻 CLI Reference

| Command | Description |
| :--- | :--- |
| `python flowmodoro.py` | Start an interactive focus session |
| `python flowmodoro.py -t "Task Name"` | Start directly with a pre-set task name |
| `python flowmodoro.py --stats` (or `-s`) | View the analytics dashboard & 7-day progress |
| `python flowmodoro.py --undo` (or `-u`) | Quickly delete the most recent session |
| `python flowmodoro.py --delete` (or `-d`) | Open interactive menu to pick and delete sessions |

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
  • Markdown Vault  : flowmodoro_log.md
============================================================
```

---

## 📝 Data Storage & Markdown Sync

Every completed or deleted session automatically updates both local files:

### 1. `flowmodoro_data.jsonl` (Source of Truth)
```json
{"date": "2026-08-21", "start_time": "06:00:15", "end_time": "07:15:40", "focus_seconds": 4525.0, "break_seconds": 905.0, "task": "Advanced Algorithms"}
```

### 2. `flowmodoro_log.md` (Obsidian / Notes Journal)
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

To sustainably execute 6 daily hours of deep work without cognitive collapse:

1. **6:00 AM – 8:30 AM (Peak Analytical Block):** Tackle the hardest problem or primary theoretical bottleneck. Zero communication, notifications, or tab-switching.
2. **8:30 AM – 8:50 AM (Physical Reset):** Hydrate, walk outside, stretch. Strictly no social media or reading feeds.
3. **8:50 AM – 10:30 AM (Deep Execution Block):** Problem sets, coding, or rigorous writing.
4. **10:30 AM – 10:50 AM (Rest / Nutrition):** Light fuel, screen-free recovery.
5. **10:50 AM – 12:00 PM (Review & Synthesis):** Anki/spaced repetition, notes integration, and organizing tomorrow's priorities.

---

## 🛠️ Architecture & Platform Audio Handling

| Platform | Audio Mechanism | Behavior |
| :--- | :--- | :--- |
| **Windows** | `ctypes.windll.kernel32.Beep` / PowerShell | Direct hardware tone ($1000\text{ Hz}, 350\text{ ms}$) |
| **macOS** | `afplay /System/Library/Sounds/Glass.aiff` | Native macOS audio playback |
| **Linux** | `paplay` / `aplay` | PulseAudio / ALSA sound player |
| **WSL** | Routed to `powershell.exe` | Seamless alert pass-through to host OS |
