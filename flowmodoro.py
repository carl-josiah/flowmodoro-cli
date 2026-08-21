import os
import sys
import time
import json
import subprocess
import platform
import threading
import argparse
from datetime import datetime, date, timedelta

BREAK_RATIO = 0.2  # 20% ratio: 50m focus -> 10m break
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_DIR, "flowmodoro_config.json")

# --- Configuration Management (Persistent Path) ---
def get_config():
    """Loads configuration or creates default pointing to the script directory."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"target_dir": SCRIPT_DIR}

def save_config(config_data):
    """Saves persistent configuration to disk."""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=2)

def set_persistent_directory(raw_path):
    """Validates and updates the persistent target directory."""
    expanded_path = os.path.abspath(os.path.expanduser(raw_path.strip()))
    if not os.path.exists(expanded_path):
        os.makedirs(expanded_path, exist_ok=True)
        print(f"\033[0;32m✓ Created new directory:\033[0m {expanded_path}")
    
    config = get_config()
    config["target_dir"] = expanded_path
    save_config(config)
    print(f"\033[1;32m✓ Successfully set persistent log path to:\033[0m")
    print(f"  📂 {expanded_path}")
    print(f"  All future sessions and markdown logs will save here until changed.\n")

def get_active_paths():
    """Returns active file paths for JSONL data and Markdown logs."""
    config = get_config()
    target_dir = config.get("target_dir", SCRIPT_DIR)
    
    if not os.path.exists(target_dir):
        os.makedirs(target_dir, exist_ok=True)
        
    data_file = os.path.join(target_dir, "flowmodoro_data.jsonl")
    md_file = os.path.join(target_dir, "flowmodoro_log.md")
    return target_dir, data_file, md_file

# --- Audio Alert ---
def play_single_sound():
    system = platform.system()
    sys.stdout.write('\a')
    sys.stdout.flush()

    try:
        if system == "Windows":
            import ctypes
            windll = getattr(ctypes, 'windll', None)
            if windll:
                windll.kernel32.Beep(1000, 350)
            else:
                subprocess.Popen(
                    ["powershell", "-c", "[console]::beep(1000, 350)"],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
        elif system == "Darwin":
            subprocess.Popen(
                ["afplay", "/System/Library/Sounds/Glass.aiff"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
        elif system == "Linux":
            played = False
            for cmd in [
                ["paplay", "/usr/share/sounds/freedesktop/stereo/complete.oga"],
                ["aplay", "/usr/share/sounds/alsa/Front_Center.wav"]
            ]:
                if os.system(f"which {cmd[0]} > /dev/null 2>&1") == 0:
                    subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    played = True
                    break
            if not played and "microsoft" in platform.uname().release.lower():
                subprocess.Popen(
                    ["powershell.exe", "-c", "[console]::beep(1000, 350)"],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
    except Exception:
        pass

def _alarm_loop(stop_event):
    while not stop_event.is_set():
        play_single_sound()
        stop_event.wait(1.5)

def ring_alarm_until_dismissed():
    stop_event = threading.Event()
    alarm_thread = threading.Thread(target=_alarm_loop, args=(stop_event,), daemon=True)
    alarm_thread.start()

    print("\n\n\033[1;33m>>> Break complete! Press [Enter] to dismiss alarm and start next session... <<<\033[0m")
    try:
        input()
    except KeyboardInterrupt:
        pass
    finally:
        stop_event.set()
        alarm_thread.join()

# --- Formatting ---
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def format_time(seconds):
    mins, secs = divmod(int(seconds), 60)
    hrs, mins = divmod(mins, 60)
    if hrs > 0:
        return f"{hrs:02d}h {mins:02d}m {secs:02d}s"
    return f"{mins:02d}m {secs:02d}s"

def format_short_time(seconds):
    mins, secs = divmod(int(seconds), 60)
    hrs, mins = divmod(mins, 60)
    if hrs > 0:
        return f"{hrs:02d}:{mins:02d}:{secs:02d}"
    return f"{mins:02d}:{secs:02d}"

# --- Data Persistence & Markdown Sync ---
def load_all_sessions():
    _, data_file, _ = get_active_paths()
    if not os.path.exists(data_file):
        return []
    sessions = []
    with open(data_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                try:
                    sessions.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue
    return sessions

def overwrite_all_sessions(sessions):
    _, data_file, _ = get_active_paths()
    with open(data_file, "w", encoding="utf-8") as f:
        for s in sessions:
            f.write(json.dumps(s) + "\n")
    sync_markdown_report()

def save_session(start_dt, end_dt, focus_seconds, break_seconds, task_name="Deep Work"):
    _, data_file, _ = get_active_paths()
    record = {
        "date": start_dt.strftime("%Y-%m-%d"),
        "start_time": start_dt.strftime("%H:%M:%S"),
        "end_time": end_dt.strftime("%H:%M:%S"),
        "focus_seconds": round(focus_seconds, 2),
        "break_seconds": round(break_seconds, 2),
        "task": task_name
    }
    with open(data_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
    sync_markdown_report()

def sync_markdown_report():
    sessions = load_all_sessions()
    _, _, md_file = get_active_paths()
    
    if not sessions:
        with open(md_file, "w", encoding="utf-8") as f:
            f.write("# ⚡ Flowmodoro Deep Work Journal\n\n")
            f.write(f"> *Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
            f.write("*No focus sessions recorded yet.*\n")
        return

    total_focus = sum(s["focus_seconds"] for s in sessions)
    total_breaks = sum(s["break_seconds"] for s in sessions)
    session_count = len(sessions)
    
    by_date = {}
    for s in sessions:
        d = s["date"]
        by_date.setdefault(d, []).append(s)

    today_str = date.today().strftime("%Y-%m-%d")
    today_sessions = by_date.get(today_str, [])
    today_focus = sum(s["focus_seconds"] for s in today_sessions)

    with open(md_file, "w", encoding="utf-8") as f:
        f.write("# ⚡ Flowmodoro Deep Work Journal\n\n")
        f.write(f"> *Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
        
        f.write("## 📊 Overview Metrics\n\n")
        f.write("| Metric | Value |\n")
        f.write("| :--- | :--- |\n")
        f.write(f"| **Today's Focus** | `{format_time(today_focus)}` ({len(today_sessions)} sessions) |\n")
        f.write(f"| **All-Time Focus** | `{format_time(total_focus)}` |\n")
        f.write(f"| **Total Rest Earned** | `{format_time(total_breaks)}` |\n")
        f.write(f"| **Total Completed Cycles** | `{session_count}` |\n")
        f.write(f"| **Active Days** | `{len(by_date)}` |\n\n")
        
        f.write("## 📝 Session Logs\n\n")
        f.write("| Date | Task / Topic | Start | End | Focus | Earned Break |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- | :--- |\n")
        
        for s in reversed(sessions):
            f_time = format_short_time(s["focus_seconds"])
            b_time = format_short_time(s["break_seconds"])
            f.write(f"| {s['date']} | {s.get('task', 'Deep Work')} | {s['start_time']} | {s['end_time']} | `{f_time}` | `{b_time}` |\n")

# --- Deletion Handlers ---
def delete_last_session():
    _, _, md_file = get_active_paths()
    sessions = load_all_sessions()
    if not sessions:
        print("\n\033[1;31mNo sessions available to remove.\033[0m")
        return

    last = sessions[-1]
    print(f"\nMost recent session: [{last['date']} {last['start_time']}-{last['end_time']}] '{last.get('task')}' ({format_short_time(last['focus_seconds'])})")
    confirm = input("Are you sure you want to remove this session? [y/N]: ").strip().lower()
    
    if confirm == 'y':
        removed = sessions.pop()
        overwrite_all_sessions(sessions)
        print(f"\033[1;32m✓ Removed session '{removed.get('task')}' and resynced {md_file}\033[0m\n")
    else:
        print("Deletion canceled.\n")

def interactive_delete_session():
    _, _, md_file = get_active_paths()
    sessions = load_all_sessions()
    if not sessions:
        print("\n\033[1;31mNo sessions recorded yet.\033[0m")
        return

    clear_screen()
    print("=" * 65)
    print("                🗑️  DELETE / MANAGE SESSIONS")
    print("=" * 65)
    
    display_limit = min(20, len(sessions))
    start_idx = len(sessions) - display_limit
    
    print(f"\nShowing last {display_limit} sessions (newest at bottom):\n")
    print("  #   | Date       | Time Window     | Task                 | Focus")
    print("  ----+------------+-----------------+----------------------+----------")
    for i in range(start_idx, len(sessions)):
        s = sessions[i]
        t_window = f"{s['start_time']} - {s['end_time']}"
        task = (s.get('task', 'Deep Work')[:20])
        f_dur = format_short_time(s['focus_seconds'])
        print(f"  {i+1:<3} | {s['date']} | {t_window:<15} | {task:<20} | {f_dur}")

    print("=" * 65)
    choice = input(f"\nEnter session number to delete (1-{len(sessions)}) or 'q' to cancel: ").strip().lower()
    
    if choice == 'q' or not choice:
        print("Deletion canceled.\n")
        return
        
    try:
        target_idx = int(choice) - 1
        if 0 <= target_idx < len(sessions):
            target = sessions[target_idx]
            confirm = input(f"Delete [{target['date']} {target['start_time']}] '{target.get('task')}'? [y/N]: ").strip().lower()
            if confirm == 'y':
                removed = sessions.pop(target_idx)
                overwrite_all_sessions(sessions)
                print(f"\033[1;32m✓ Successfully deleted session #{target_idx+1} and updated {md_file}\033[0m\n")
            else:
                print("Deletion canceled.\n")
        else:
            print("\033[1;31mInvalid session number.\033[0m\n")
    except ValueError:
        print("\033[1;31mPlease enter a valid numeric ID.\033[0m\n")

# --- Dashboard & CLI View ---
def render_ascii_bar(progress, width=20):
    filled = int(round(progress * width))
    filled = min(width, max(0, filled))
    return f"[{'█' * filled}{'░' * (width - filled)}] {int(progress * 100)}%"

def display_dashboard():
    target_dir, _, md_file = get_active_paths()
    sessions = load_all_sessions()
    clear_screen()
    print("=" * 60)
    print("             ⚡ FLOWMODORO ANALYTICS DASHBOARD ⚡")
    print("=" * 60)

    if not sessions:
        print("\nNo recorded sessions found yet in current directory.")
        print(f"📂 Active Path: \033[0;36m{target_dir}\033[0m\n")
        return

    today_dt = date.today()
    today_str = today_dt.strftime("%Y-%m-%d")
    
    daily_totals = {}
    for s in sessions:
        d = s["date"]
        daily_totals[d] = daily_totals.get(d, 0) + s["focus_seconds"]

    today_focus = daily_totals.get(today_str, 0)
    total_focus = sum(s["focus_seconds"] for s in sessions)
    DAILY_GOAL_SECONDS = 6 * 3600
    goal_ratio = min(1.0, today_focus / DAILY_GOAL_SECONDS)

    print(f"\n📅 Today ({today_str}):")
    print(f"  • Focus Logged : \033[1;32m{format_time(today_focus)}\033[0m")
    print(f"  • Daily 6h Goal: {render_ascii_bar(goal_ratio)} ({format_short_time(today_focus)} / 06:00:00)")

    print("\n📈 Last 7 Days Activity:")
    print("  Date       | Focus Time  | Daily 6h Target")
    print("  -----------+-------------+-----------------------------")
    for i in range(6, -1, -1):
        day_date = today_dt - timedelta(days=i)
        day_str = day_date.strftime("%Y-%m-%d")
        sec = daily_totals.get(day_str, 0)
        bar = render_ascii_bar(min(1.0, sec / DAILY_GOAL_SECONDS), width=12)
        mark = " (Today)" if day_str == today_str else ""
        print(f"  {day_str} | {format_short_time(sec):<11} | {bar}{mark}")

    sorted_days = sorted([datetime.strptime(d, "%Y-%m-%d").date() for d in daily_totals.keys()])
    current_streak = 0
    check_day = today_dt
    
    if today_dt not in sorted_days:
        check_day = today_dt - timedelta(days=1)
        
    while check_day in sorted_days:
        current_streak += 1
        check_day -= timedelta(days=1)

    print("\n🏆 Summary Highlights:")
    print(f"  • Total Sessions  : {len(sessions)}")
    print(f"  • Lifetime Focus  : {format_time(total_focus)}")
    print(f"  • Current Streak  : \033[1;33m{current_streak} day(s)\033[0m")
    print(f"  • Active Directory: \033[0;36m{target_dir}\033[0m")
    print(f"  • Markdown Vault  : \033[0;36m{md_file}\033[0m")
    print("=" * 60 + "\n")

# --- Session Run Loops ---
def run_focus_session(task_name="Deep Work"):
    target_dir, _, md_file = get_active_paths()
    clear_screen()
    print("=== FLOWMODORO: FOCUS MODE ===")
    print(f"🎯 Objective: \033[1;36m{task_name}\033[0m")
    print(f"📂 Logging to: \033[0;36m{md_file}\033[0m")
    print("Tracking deep work. Press [Ctrl + C] when your flow breaks.\n")
    
    start_dt = datetime.now()
    start_time = time.time()
    try:
        while True:
            elapsed = time.time() - start_time
            sys.stdout.write(f"\rFocus Time: \033[1;32m{format_short_time(elapsed)}\033[0m")
            sys.stdout.flush()
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    
    end_dt = datetime.now()
    play_single_sound()
    total_focus = time.time() - start_time
    print("\n\nSession paused.")
    return total_focus, start_dt, end_dt

def run_break_session(break_seconds):
    clear_screen()
    print("=== FLOWMODORO: EARNED REST ===")
    print("Step away from the screen, hydrate, and relax. [Ctrl + C] to skip.\n")
    
    remaining = int(break_seconds)
    try:
        while remaining > 0:
            sys.stdout.write(f"\rBreak Remaining: \033[1;34m{format_short_time(remaining)}\033[0m")
            sys.stdout.flush()
            time.sleep(1)
            remaining -= 1
        ring_alarm_until_dismissed()
    except KeyboardInterrupt:
        print("\n\nBreak skipped early.")

def main():
    parser = argparse.ArgumentParser(description="Flowmodoro CLI with Persistent Logging Directory & Markdown Sync")
    parser.add_argument("--path", "-p", type=str, help="Permanently set the storage directory for logs and markdown files")
    parser.add_argument("--where", "-w", action="store_true", help="Print the currently configured storage directory")
    parser.add_argument("--stats", "-s", action="store_true", help="Display the deep work analytics dashboard")
    parser.add_argument("--task", "-t", type=str, default="Deep Work", help="Set the task/topic name for the session")
    parser.add_argument("--undo", "-u", action="store_true", help="Quickly remove the most recently logged session")
    parser.add_argument("--delete", "-d", action="store_true", help="Interactively browse and delete specific sessions")
    args = parser.parse_args()

    # 1. Update Persistent Directory
    if args.path:
        set_persistent_directory(args.path)
        return

    # 2. Check Active Directory
    if args.where:
        target_dir, data_file, md_file = get_active_paths()
        print(f"\n📂 Active Storage Directory: \033[1;36m{target_dir}\033[0m")
        print(f"📄 Markdown Journal       : \033[0;32m{md_file}\033[0m")
        print(f"💾 JSONL Data Store       : \033[0;32m{data_file}\033[0m\n")
        return

    # 3. Stats Dashboard
    if args.stats:
        display_dashboard()
        return

    # 4. Deletion Workflows
    if args.undo:
        delete_last_session()
        return

    if args.delete:
        interactive_delete_session()
        return

    # 5. Session Execution
    target_dir, data_file, md_file = get_active_paths()
    print(f"\033[0;34m[Storage Path: {target_dir}]\033[0m")
    
    task = args.task
    if task == "Deep Work":
        prompt = input("Enter focus task/topic (Press Enter for 'Deep Work'): ").strip()
        if prompt:
            task = prompt

    total_day_focus = 0
    while True:
        focus_seconds, start_dt, end_dt = run_focus_session(task_name=task)
        total_day_focus += focus_seconds
        earned_break = focus_seconds * BREAK_RATIO
        
        save_session(start_dt, end_dt, focus_seconds, earned_break, task_name=task)
        
        print(f"Completed Focus:   {format_short_time(focus_seconds)}")
        print(f"Earned Recovery:   {format_short_time(earned_break)}")
        print(f"Total Today:       {format_time(total_day_focus)}")
        print(f"\033[0;32m✓ Saved to {md_file}\033[0m")
        
        choice = input("\nStart earned break now? [Y/n/q]: ").strip().lower()
        if choice == 'q':
            print("Session ended. Great work today!")
            break
        elif choice != 'n':
            run_break_session(earned_break)

if __name__ == "__main__":
    main()
