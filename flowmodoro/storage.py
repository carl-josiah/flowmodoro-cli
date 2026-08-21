import os
import json
import csv
from datetime import datetime, date
from .config import get_active_paths

def format_time(seconds):
    mins, secs = divmod(int(seconds), 60)
    hrs, mins = divmod(mins, 60)
    return f"{hrs:02d}h {mins:02d}m {secs:02d}s" if hrs > 0 else f"{mins:02d}m {secs:02d}s"

def format_short_time(seconds):
    mins, secs = divmod(int(seconds), 60)
    hrs, mins = divmod(mins, 60)
    return f"{hrs:02d}:{mins:02d}:{secs:02d}" if hrs > 0 else f"{mins:02d}:{secs:02d}"

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
            f.write("# ⚡ Flowmodoro Deep Work Journal\n\n*No focus sessions recorded yet.*\n")
        return

    total_focus = sum(s["focus_seconds"] for s in sessions)
    total_breaks = sum(s["break_seconds"] for s in sessions)
    by_date = {}
    for s in sessions:
        by_date.setdefault(s["date"], []).append(s)

    today_str = date.today().strftime("%Y-%m-%d")
    today_sessions = by_date.get(today_str, [])
    today_focus = sum(s["focus_seconds"] for s in today_sessions)

    with open(md_file, "w", encoding="utf-8") as f:
        f.write("# ⚡ Flowmodoro Deep Work Journal\n\n")
        f.write(f"> *Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
        f.write("## 📊 Overview Metrics\n\n")
        f.write("| Metric | Value |\n| :--- | :--- |\n")
        f.write(f"| **Today's Focus** | `{format_time(today_focus)}` ({len(today_sessions)} sessions) |\n")
        f.write(f"| **All-Time Focus** | `{format_time(total_focus)}` |\n")
        f.write(f"| **Total Rest Earned** | `{format_time(total_breaks)}` |\n")
        f.write(f"| **Total Completed Cycles** | `{len(sessions)}` |\n")
        f.write(f"| **Active Days** | `{len(by_date)}` |\n\n")
        f.write("## 📝 Session Logs\n\n| Date | Task / Topic | Start | End | Focus | Earned Break |\n| :--- | :--- | :--- | :--- | :--- | :--- |\n")
        for s in reversed(sessions):
            f.write(f"| {s['date']} | {s.get('task', 'Deep Work')} | {s['start_time']} | {s['end_time']} | `{format_short_time(s['focus_seconds'])}` | `{format_short_time(s['break_seconds'])}` |\n")

def delete_last_session():
    _, _, md_file = get_active_paths()
    sessions = load_all_sessions()
    if not sessions:
        print("\n\033[1;31mNo sessions available to remove.\033[0m\n")
        return
    last = sessions[-1]
    print(f"\nMost recent session: [{last['date']} {last['start_time']}-{last['end_time']}] '{last.get('task')}' ({format_short_time(last['focus_seconds'])})")
    if input("Are you sure you want to remove this session? [y/N]: ").strip().lower() == 'y':
        removed = sessions.pop()
        overwrite_all_sessions(sessions)
        print(f"\033[1;32m✓ Removed session '{removed.get('task')}' and resynced {md_file}\033[0m\n")

def interactive_delete_session():
    _, _, md_file = get_active_paths()
    sessions = load_all_sessions()
    if not sessions:
        print("\n\033[1;31mNo sessions recorded yet.\033[0m\n")
        return
    os.system('cls' if os.name == 'nt' else 'clear')
    print("=" * 65 + "\n                🗑️  DELETE / MANAGE SESSIONS\n" + "=" * 65)
    display_limit = min(20, len(sessions))
    start_idx = len(sessions) - display_limit
    print(f"\nShowing last {display_limit} sessions (newest at bottom):\n")
    print("  #   | Date       | Time Window     | Task                 | Focus\n  ----+------------+-----------------+----------------------+----------")
    for i in range(start_idx, len(sessions)):
        s = sessions[i]
        print(f"  {i+1:<3} | {s['date']} | {s['start_time']} - {s['end_time']:<8} | {s.get('task', 'Deep Work')[:20]:<20} | {format_short_time(s['focus_seconds'])}")
    print("=" * 65)
    choice = input(f"\nEnter session number to delete (1-{len(sessions)}) or 'q' to cancel: ").strip().lower()
    if choice != 'q' and choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(sessions):
            if input(f"Delete session #{idx+1}? [y/N]: ").strip().lower() == 'y':
                sessions.pop(idx)
                overwrite_all_sessions(sessions)
                print(f"\033[1;32m✓ Deleted session #{idx+1} and resynced {md_file}\033[0m\n")

def export_data(destination_file):
    """Exports session logs to CSV or JSON format."""
    sessions = load_all_sessions()
    if not sessions:
        print("\n\033[1;31mNo session logs found to export.\033[0m\n")
        return

    dest_path = os.path.abspath(os.path.expanduser(destination_file.strip()))
    ext = os.path.splitext(dest_path)[1].lower()

    try:
        if ext == ".json":
            with open(dest_path, "w", encoding="utf-8") as f:
                json.dump(sessions, f, indent=2)
        else:  # Default to CSV
            if not ext.endswith(".csv"):
                dest_path += ".csv"
            with open(dest_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["date", "task", "start_time", "end_time", "focus_seconds", "break_seconds"])
                writer.writeheader()
                for s in sessions:
                    writer.writerow({
                        "date": s.get("date"),
                        "task": s.get("task", "Deep Work"),
                        "start_time": s.get("start_time"),
                        "end_time": s.get("end_time"),
                        "focus_seconds": s.get("focus_seconds"),
                        "break_seconds": s.get("break_seconds")
                    })
        print(f"\033[1;32m✓ Exported {len(sessions)} session(s) successfully to:\033[0m\n  📂 {dest_path}\n")
    except Exception as e:
        print(f"\033[1;31mExport failed: {e}\033[0m\n")
