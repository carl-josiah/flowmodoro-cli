import os
import json
import csv
import math
from datetime import datetime, date
from .config import get_active_paths

def format_time(seconds):
    try:
        if seconds is None or not isinstance(seconds, (int, float)) or not math.isfinite(seconds):
            sec_val = 0
        else:
            sec_val = max(0, int(seconds))
    except Exception:
        sec_val = 0

    mins, secs = divmod(sec_val, 60)
    hrs, mins = divmod(mins, 60)
    return f"{hrs:02d}h {mins:02d}m {secs:02d}s" if hrs > 0 else f"{mins:02d}m {secs:02d}s"

def format_short_time(seconds):
    try:
        if seconds is None or not isinstance(seconds, (int, float)) or not math.isfinite(seconds):
            sec_val = 0
        else:
            sec_val = max(0, int(seconds))
    except Exception:
        sec_val = 0

    mins, secs = divmod(sec_val, 60)
    hrs, mins = divmod(mins, 60)
    return f"{hrs:02d}:{mins:02d}:{secs:02d}" if hrs > 0 else f"{mins:02d}:{secs:02d}"

def load_all_sessions():
    _, data_file, _ = get_active_paths()
    if not os.path.exists(data_file):
        return []
    sessions = []
    try:
        with open(data_file, "r", encoding="utf-8") as f:
            for line in f:
                line_str = line.strip()
                if line_str:
                    try:
                        record = json.loads(line_str)
                        if isinstance(record, dict):
                            # Sanitize fields
                            focus_sec = record.get("focus_seconds")
                            if not isinstance(focus_sec, (int, float)) or not math.isfinite(focus_sec) or focus_sec < 0:
                                record["focus_seconds"] = 0.0
                            else:
                                record["focus_seconds"] = float(focus_sec)

                            break_sec = record.get("break_seconds")
                            if not isinstance(break_sec, (int, float)) or not math.isfinite(break_sec) or break_sec < 0:
                                record["break_seconds"] = 0.0
                            else:
                                record["break_seconds"] = float(break_sec)

                            if not isinstance(record.get("date"), str) or not record["date"].strip():
                                record["date"] = date.today().strftime("%Y-%m-%d")

                            if not isinstance(record.get("start_time"), str):
                                record["start_time"] = "00:00:00"

                            if not isinstance(record.get("end_time"), str):
                                record["end_time"] = "00:00:00"

                            if not isinstance(record.get("task"), str):
                                record["task"] = "Deep Work"

                            sessions.append(record)
                    except json.JSONDecodeError:
                        continue
    except Exception:
        pass
    return sessions

def overwrite_all_sessions(sessions):
    _, data_file, _ = get_active_paths()
    try:
        with open(data_file, "w", encoding="utf-8") as f:
            for s in sessions:
                if isinstance(s, dict):
                    f.write(json.dumps(s) + "\n")
        sync_markdown_report()
    except Exception as e:
        print(f"\033[1;31mError saving session store: {e}\033[0m\n")

def save_session(start_dt, end_dt, focus_seconds, break_seconds, task_name="Deep Work"):
    _, data_file, _ = get_active_paths()
    record = {
        "date": start_dt.strftime("%Y-%m-%d"),
        "start_time": start_dt.strftime("%H:%M:%S"),
        "end_time": end_dt.strftime("%H:%M:%S"),
        "focus_seconds": round(max(0.0, float(focus_seconds)), 2),
        "break_seconds": round(max(0.0, float(break_seconds)), 2),
        "task": str(task_name) if task_name else "Deep Work"
    }
    try:
        with open(data_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
        sync_markdown_report()
    except Exception as e:
        print(f"\033[1;31mError appending session: {e}\033[0m\n")

def sync_markdown_report():
    sessions = load_all_sessions()
    _, _, md_file = get_active_paths()
    try:
        if not sessions:
            with open(md_file, "w", encoding="utf-8") as f:
                f.write("# ⚡ Flowmodoro Deep Work Journal\n\n*No focus sessions recorded yet.*\n")
            return

        total_focus = sum(s.get("focus_seconds", 0.0) for s in sessions)
        total_breaks = sum(s.get("break_seconds", 0.0) for s in sessions)
        by_date = {}
        by_task = {}
        for s in sessions:
            d = s.get("date", date.today().strftime("%Y-%m-%d"))
            t = s.get("task", "Deep Work")
            f_sec = s.get("focus_seconds", 0.0)
            by_date.setdefault(d, []).append(s)
            by_task[t] = by_task.get(t, 0.0) + f_sec

        today_str = date.today().strftime("%Y-%m-%d")
        today_sessions = by_date.get(today_str, [])
        today_focus = sum(s.get("focus_seconds", 0.0) for s in today_sessions)

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

            if by_task and total_focus > 0:
                f.write("## 🎯 Focus Share by Topic\n\n| Objective / Task | Focus Time | Share (%) |\n| :--- | :--- | :--- |\n")
                sorted_tasks = sorted(by_task.items(), key=lambda x: x[1], reverse=True)
                for t_name, t_sec in sorted_tasks:
                    pct = (t_sec / total_focus) * 100
                    f.write(f"| {t_name} | `{format_time(t_sec)}` | `{pct:.1f}%` |\n")
                f.write("\n")

            f.write("## 📝 Session Logs\n\n| Date | Task / Topic | Start | End | Focus | Earned Break |\n| :--- | :--- | :--- | :--- | :--- | :--- |\n")
            for s in reversed(sessions):
                date_val = s.get('date', '')
                task_val = s.get('task', 'Deep Work')
                start_val = s.get('start_time', '00:00:00')
                end_val = s.get('end_time', '00:00:00')
                f_sec = s.get('focus_seconds', 0.0)
                b_sec = s.get('break_seconds', 0.0)
                f.write(f"| {date_val} | {task_val} | {start_val} | {end_val} | `{format_short_time(f_sec)}` | `{format_short_time(b_sec)}` |\n")

    except Exception as e:
        print(f"\033[1;31mError generating markdown report: {e}\033[0m\n")

def delete_last_session():
    _, _, md_file = get_active_paths()
    sessions = load_all_sessions()
    if not sessions:
        print("\n\033[1;31mNo sessions available to remove.\033[0m\n")
        return
    last = sessions[-1]
    print(f"\nMost recent session: [{last.get('date')} {last.get('start_time')}-{last.get('end_time')}] '{last.get('task')}' ({format_short_time(last.get('focus_seconds'))})")
    try:
        choice = input("Are you sure you want to remove this session? [y/N]: ").strip().lower()
        if choice == 'y':
            removed = sessions.pop()
            overwrite_all_sessions(sessions)
            print(f"\033[1;32m✓ Removed session '{removed.get('task')}' and resynced {md_file}\033[0m\n")
    except (KeyboardInterrupt, EOFError):
        print("\nOperation canceled.\n")

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
        d_val = s.get('date', 'N/A')
        st_val = s.get('start_time', '00:00:00')
        et_val = s.get('end_time', '00:00:00')
        t_val = str(s.get('task', 'Deep Work'))[:20]
        f_val = format_short_time(s.get('focus_seconds', 0))
        print(f"  {i+1:<3} | {d_val} | {st_val} - {et_val:<8} | {t_val:<20} | {f_val}")
    print("=" * 65)
    try:
        choice = input(f"\nEnter session number to delete (1-{len(sessions)}) or 'q' to cancel: ").strip().lower()
        if choice not in ('q', ''):
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(sessions):
                    confirm = input(f"Delete session #{idx+1}? [y/N]: ").strip().lower()
                    if confirm == 'y':
                        sessions.pop(idx)
                        overwrite_all_sessions(sessions)
                        print(f"\033[1;32m✓ Deleted session #{idx+1} and resynced {md_file}\033[0m\n")
                else:
                    print("\033[1;31mError: Session number out of range.\033[0m\n")
            else:
                print("\033[1;31mError: Please enter a valid numerical session number.\033[0m\n")
    except (KeyboardInterrupt, EOFError):
        print("\nOperation canceled.\n")

def export_data(destination_file):
    """Exports session logs to CSV or JSON format."""
    if not destination_file or not isinstance(destination_file, str) or "\0" in destination_file:
        print("\033[1;31mExport failed: Invalid destination path specified.\033[0m\n")
        return

    cleaned = destination_file.strip()
    if not cleaned:
        print("\033[1;31mExport failed: Destination file path cannot be empty.\033[0m\n")
        return

    sessions = load_all_sessions()
    if not sessions:
        print("\n\033[1;31mNo session logs found to export.\033[0m\n")
        return

    try:
        dest_path = os.path.abspath(os.path.expanduser(cleaned))
        if os.path.isdir(dest_path):
            print(f"\033[1;31mExport failed: Path '{dest_path}' is a directory, not a file.\033[0m\n")
            return

        parent_dir = os.path.dirname(dest_path)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)

        ext = os.path.splitext(dest_path)[1].lower()

        if ext == ".json":
            with open(dest_path, "w", encoding="utf-8") as f:
                json.dump(sessions, f, indent=2)
        else:  # Default to CSV
            if not ext.endswith(".csv"):
                dest_path += ".csv"
            with open(dest_path, "w", newline="", encoding="utf-8") as f:
                fields = ["date", "task", "start_time", "end_time", "focus_seconds", "focus_minutes", "focus_hours", "break_seconds", "break_minutes"]
                writer = csv.DictWriter(f, fieldnames=fields)
                writer.writeheader()
                for s in sessions:
                    f_sec = s.get("focus_seconds", 0.0)
                    b_sec = s.get("break_seconds", 0.0)
                    writer.writerow({
                        "date": s.get("date"),
                        "task": s.get("task", "Deep Work"),
                        "start_time": s.get("start_time"),
                        "end_time": s.get("end_time"),
                        "focus_seconds": round(f_sec, 2),
                        "focus_minutes": round(f_sec / 60.0, 2),
                        "focus_hours": round(f_sec / 3600.0, 2),
                        "break_seconds": round(b_sec, 2),
                        "break_minutes": round(b_sec / 60.0, 2)
                    })
        print(f"\033[1;32m✓ Exported {len(sessions)} session(s) successfully to:\033[0m\n  📂 {dest_path}\n")

    except Exception as e:
        print(f"\033[1;31mExport failed: {e}\033[0m\n")

