import os
import sys
import time
import math
from datetime import datetime
from .config import get_active_paths, get_config
from .audio import trigger_alert, ring_alarm_until_dismissed
from .storage import format_short_time, format_time, normalize_task_name

def run_focus_session(task_name="DEEP_WORK"):
    _, _, md_file = get_active_paths()
    os.system('cls' if os.name == 'nt' else 'clear')
    safe_task = normalize_task_name(task_name)
    print("=== FLOWMODORO: FOCUS MODE ===")
    print(f"🎯 Objective: \033[1;36m{safe_task}\033[0m\n📂 Logging to: \033[0;36m{md_file}\033[0m")
    print("Tracking deep work. Press [Ctrl + C] when your flow breaks.\n")
    
    start_dt = datetime.now()
    start_time = time.time()
    trigger_alert("focus_sound")
    try:

        while True:
            elapsed = max(0.0, time.time() - start_time)
            sys.stdout.write(f"\rFocus Time: \033[1;32m{format_short_time(elapsed)}\033[0m")
            sys.stdout.flush()
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    
    end_dt = datetime.now()
    trigger_alert("start_sound")
    print("\n\nSession paused.")
    elapsed_total = max(0.0, time.time() - start_time)
    return elapsed_total, start_dt, end_dt

def run_break_session(break_seconds):
    if not isinstance(break_seconds, (int, float)) or not math.isfinite(break_seconds) or break_seconds <= 0:
        print("No earned break time available.")
        return

    config = get_config()
    max_mins = config.get("max_break_minutes")
    
    capped_note = ""
    actual_break = max(0.0, float(break_seconds))
    if isinstance(max_mins, (int, float)) and math.isfinite(max_mins) and max_mins > 0:
        max_sec = max_mins * 60
        if actual_break > max_sec:
            actual_break = max_sec
            capped_note = f" (Capped from {format_short_time(break_seconds)} by max-break limit)"

    os.system('cls' if os.name == 'nt' else 'clear')
    print("=== FLOWMODORO: EARNED REST ===")
    print(f"Break Duration: \033[1;34m{format_short_time(actual_break)}\033[0m{capped_note}")
    print("Step away from the screen, hydrate, and relax. [Ctrl + C] to skip.\n")

    remaining = int(actual_break)
    try:
        while remaining > 0:
            sys.stdout.write(f"\rBreak Remaining: \033[1;34m{format_short_time(remaining)}\033[0m")
            sys.stdout.flush()
            time.sleep(1)
            remaining -= 1
        ring_alarm_until_dismissed()
    except KeyboardInterrupt:
        print("\n\nBreak skipped early.")

