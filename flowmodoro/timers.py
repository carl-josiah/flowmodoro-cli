import os
import sys
import time
from datetime import datetime
from .config import get_active_paths
from .audio import trigger_alert, ring_alarm_until_dismissed
from .storage import format_short_time

def run_focus_session(task_name="Deep Work"):
    _, _, md_file = get_active_paths()
    os.system('cls' if os.name == 'nt' else 'clear')
    print("=== FLOWMODORO: FOCUS MODE ===")
    print(f"🎯 Objective: \033[1;36m{task_name}\033[0m\n📂 Logging to: \033[0;36m{md_file}\033[0m")
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
    trigger_alert("start_sound")
    print("\n\nSession paused.")
    return time.time() - start_time, start_dt, end_dt

def run_break_session(break_seconds):
    os.system('cls' if os.name == 'nt' else 'clear')
    print("=== FLOWMODORO: EARNED REST ===\nStep away from the screen, hydrate, and relax. [Ctrl + C] to skip.\n")
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
