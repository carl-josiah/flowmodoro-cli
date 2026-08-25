import os
import math
from datetime import date, timedelta, datetime
from .config import get_active_paths, get_config
from .storage import load_all_sessions, format_time, format_short_time, normalize_task_name

def render_ascii_bar(progress, width=20):
    try:
        if progress is None or not isinstance(progress, (int, float)) or not math.isfinite(progress):
            p = 0.0
        else:
            p = max(0.0, min(1.0, float(progress)))
    except Exception:
        p = 0.0

    filled = int(round(p * width))
    filled = min(width, max(0, filled))
    return f"[{'█' * filled}{'░' * (width - filled)}] {int(p * 100)}%"

def render_activity_heatmap(daily_totals, target_seconds):
    today = date.today()
    output = []
    t_sec = float(target_seconds) if (isinstance(target_seconds, (int, float)) and math.isfinite(target_seconds) and target_seconds > 0) else 21600.0

    for i in range(27, -1, -1):
        d_str = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        sec = daily_totals.get(d_str, 0)
        ratio = sec / t_sec if t_sec > 0 else 0
        if ratio == 0:
            output.append("·")
        elif ratio < 0.35:
            output.append("\033[0;32m░\033[0m")
        elif ratio < 0.70:
            output.append("\033[0;32m▒\033[0m")
        elif ratio < 1.0:
            output.append("\033[1;32m▓\033[0m")
        else:
            output.append("\033[1;33m█\033[0m")
    
    w1, w2, w3, w4 = "".join(output[:7]), "".join(output[7:14]), "".join(output[14:21]), "".join(output[21:])
    return f"{w1}  {w2}  {w3}  {w4}  (Today)"

def display_dashboard(filter_task=None):
    target_dir, _, md_file = get_active_paths()
    config = get_config()
    goal_hours = config.get("daily_goal_hours", 6.0)
    if not isinstance(goal_hours, (int, float)) or not math.isfinite(goal_hours) or goal_hours <= 0:
        goal_hours = 6.0

    DAILY_GOAL_SECONDS = max(1.0, float(goal_hours) * 3600)

    all_sessions = load_all_sessions()
    os.system('cls' if os.name == 'nt' else 'clear')
    print("=" * 62)
    print("               ⚡ FLOWMODORO ANALYTICS DASHBOARD ⚡")
    print("=" * 62)

    if not all_sessions:
        print(f"\nNo recorded sessions found yet.\n📂 Active Path: \033[0;36m{target_dir}\033[0m\n")
        return

    if filter_task and isinstance(filter_task, str):
        clean_filter = normalize_task_name(filter_task)
        sessions = [s for s in all_sessions if clean_filter in normalize_task_name(str(s.get("task", "")))]
        print(f"\n🎯 Filter Active: \033[1;36m'{clean_filter}'\033[0m ({len(sessions)} matching sessions)")
    else:
        sessions = all_sessions

    if not sessions:
        print(f"\nNo sessions match the filter '{filter_task}'.\n")
        return

    today_dt = date.today()
    today_str = today_dt.strftime("%Y-%m-%d")
    daily_totals = {}
    task_totals = {}
    task_counts = {}
    
    for s in sessions:
        d = s.get("date", today_str)
        t = normalize_task_name(str(s.get("task", "DEEP_WORK")))
        f_sec = s.get("focus_seconds", 0.0)
        daily_totals[d] = daily_totals.get(d, 0.0) + f_sec
        task_totals[t] = task_totals.get(t, 0.0) + f_sec
        task_counts[t] = task_counts.get(t, 0) + 1

    today_focus = daily_totals.get(today_str, 0.0)
    total_focus = sum(s.get("focus_seconds", 0.0) for s in sessions)
    goal_str = format_short_time(DAILY_GOAL_SECONDS)

    print(f"\n📅 Today ({today_str}):")
    print(f"  • Focus Logged : \033[1;32m{format_time(today_focus)}\033[0m")
    print(f"  • Daily Goal   : {render_ascii_bar(today_focus / DAILY_GOAL_SECONDS)} ({format_short_time(today_focus)} / {goal_str})")

    print(f"\n🗓️  28-Day Consistency Heatmap (Goal: {goal_hours:g}h/day):")
    print(f"  {render_activity_heatmap(daily_totals, DAILY_GOAL_SECONDS)}")
    print("  \033[2m[· 0h  ░ <35%  ▒ <70%  ▓ <100%  █ Goal Met]\033[0m")

    print(f"\n📈 Last 7 Days Activity:")
    print("  Date       | Focus Time  | Daily Target            | Goal Status")
    print("  -----------+-------------+-------------------------+------------")
    for i in range(6, -1, -1):
        d_dt = today_dt - timedelta(days=i)
        d_str = d_dt.strftime("%Y-%m-%d")
        sec = daily_totals.get(d_str, 0.0)
        mark = " (Today)" if d_str == today_str else ""
        if sec >= DAILY_GOAL_SECONDS:
            status_badge = "\033[1;32m✓ Goal Met\033[0m"
        elif d_str == today_str:
            status_badge = "\033[0;33mIn Progress\033[0m"
        else:
            status_badge = "\033[2mMissed\033[0m"
        print(f"  {d_str} | {format_short_time(sec):<11} | {render_ascii_bar(sec / DAILY_GOAL_SECONDS, width=12):<23}{mark:<8} | {status_badge}")

    if task_totals:
        print("\n🏷️  Task & Objective Breakdown:")
        print("  Task Name              | Sessions | Total Time  | Share")
        print("  -----------------------+----------+-------------+-------")
        sorted_tasks = sorted(task_totals.items(), key=lambda x: x[1], reverse=True)
        for t_name, t_sec in sorted_tasks:
            count = task_counts.get(t_name, 0)
            pct = (t_sec / total_focus) * 100 if total_focus > 0 else 0
            safe_tname = str(t_name)[:22]
            print(f"  {safe_tname:<22} | {count:<8} | {format_time(t_sec):<11} | {pct:>4.0f}%")

    # Streak logic: calculate consecutive days where daily goal was met
    goal_met_dates = set()
    for d_str, sec in daily_totals.items():
        if sec >= DAILY_GOAL_SECONDS:
            try:
                goal_met_dates.add(datetime.strptime(d_str, "%Y-%m-%d").date())
            except (ValueError, TypeError):
                pass

    current_streak = 0
    check_day = today_dt if today_dt in goal_met_dates else (today_dt - timedelta(days=1))
    while check_day in goal_met_dates:
        current_streak += 1
        check_day -= timedelta(days=1)

    print(f"\n🏆 Summary Highlights:")
    print(f"  • Daily Target    : {goal_hours:g} hour(s)/day")
    print(f"  • Total Focus     : {format_time(total_focus)} across {len(sessions)} cycle(s)")
    print(f"  • Current Streak  : \033[1;33m{current_streak} day(s)\033[0m (Goal-Met Days)")
    print(f"  • Active Vault    : \033[0;36m{md_file}\033[0m\n" + "=" * 62 + "\n")


