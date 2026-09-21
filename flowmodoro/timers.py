import os
import sys
import time
import math
from datetime import datetime
from .config import get_active_paths, get_config
from .audio import trigger_alert, ring_alarm_until_dismissed, stop_active_audio
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

def run_pomodoro_session(target_minutes=25, task_name="DEEP_WORK", cycle=1, total_cycles=4):
    target_sec = float(target_minutes) * 60.0
    _, _, md_file = get_active_paths()
    os.system('cls' if os.name == 'nt' else 'clear')
    safe_task = normalize_task_name(task_name)
    print(f"=== 🍅 POMODORO: FOCUS MODE [Cycle {cycle}/{total_cycles}] ===")
    print(f"🎯 Objective: \033[1;36m{safe_task}\033[0m\n📂 Logging to: \033[0;36m{md_file}\033[0m")
    print(f"⏱️  Target:    \033[1;32m{format_short_time(target_sec)}\033[0m ({target_minutes:g} mins)")
    print("Tracking Pomodoro focus. Press [Ctrl + C] to pause/end early.\n")

    start_dt = datetime.now()
    start_time = time.time()
    trigger_alert("focus_sound")
    completed_full = False

    try:
        while True:
            elapsed = max(0.0, time.time() - start_time)
            remaining = max(0.0, target_sec - elapsed)
            pct = min(1.0, elapsed / target_sec) if target_sec > 0 else 1.0
            bar_len = 10
            filled = min(bar_len, int(round(pct * bar_len)))
            bar = "█" * filled + "░" * (bar_len - filled)

            sys.stdout.write(f"\rFocus Remaining: \033[1;32m{format_short_time(math.ceil(remaining))}\033[0m  [{bar}] {int(pct * 100)}%")
            sys.stdout.flush()

            if remaining <= 0:
                completed_full = True
                break

            time.sleep(1)
    except KeyboardInterrupt:
        pass

    end_dt = datetime.now()
    elapsed_total = target_sec if completed_full else max(0.0, time.time() - start_time)

    if completed_full:
        from .audio import send_desktop_notification
        send_desktop_notification("🍅 Pomodoro Complete", f"Great focus on '{safe_task}'! Time for your earned break.")
        print(f"\n\n\033[1;32m🍅 Pomodoro Complete! Target reached: {format_short_time(target_sec)}\033[0m")
        ring_alarm_until_dismissed()
    else:
        trigger_alert("start_sound")
        print(f"\n\nSession paused early at {format_short_time(elapsed_total)}.")

    return elapsed_total, start_dt, end_dt, completed_full

def run_break_session(break_seconds, title="FLOWMODORO: EARNED REST"):
    if not isinstance(break_seconds, (int, float)) or not math.isfinite(break_seconds) or break_seconds <= 0:
        print("No earned break time available.")
        return True

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
    print(f"=== {title} ===")
    print(f"Break Duration: \033[1;34m{format_short_time(actual_break)}\033[0m{capped_note}")
    print("Step away from the screen, hydrate, and relax. [Ctrl + C] to cancel break.\n")

    remaining = int(actual_break)
    try:
        while remaining > 0:
            sys.stdout.write(f"\rBreak Remaining: \033[1;34m{format_short_time(remaining)}\033[0m")
            sys.stdout.flush()
            time.sleep(1)
            remaining -= 1
        ring_alarm_until_dismissed()
        return True
    except KeyboardInterrupt:
        stop_active_audio()
        print("\n\nBreak canceled early.")
        return False


