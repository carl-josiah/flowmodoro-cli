import os
from datetime import date, timedelta, datetime
from .config import get_active_paths, get_config
from .storage import load_all_sessions, format_time, format_short_time

def render_ascii_bar(progress, width=20):
    filled = int(round(progress * width))
    filled = min(width, max(0, filled))
    return f"[{'█' * filled}{'░' * (width - filled)}] {int(progress * 100)}%"

def render_activity_heatmap(daily_totals, target_seconds):
    today = date.today()
    output = []
    for i in range(27, -1, -1):
        d_str = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        sec = daily_totals.get(d_str, 0)
        ratio = sec / target_seconds if target_seconds > 0 else 0
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
    DAILY_GOAL_SECONDS = goal_hours * 3600

    all_sessions = load_all_sessions()
    os.system('cls' if os.name == 'nt' else 'clear')
    print("=" * 62)
    print("               ⚡ FLOWMODORO ANALYTICS DASHBOARD ⚡")
    print("=" * 62)

    if not all_sessions:
        print(f"\nNo recorded sessions found yet.\n📂 Active Path: \033[0;36m{target_dir}\033[0m\n")
        return

    if filter_task:
        sessions = [s for s in all_sessions if filter_task.lower() in s.get("task", "").lower()]
        print(f"\n🎯 Filter Active: \033[1;36m'{filter_task}'\033[0m ({len(sessions)} matching sessions)")
    else:
        sessions = all_sessions

    if not sessions:
        print(f"\nNo sessions match the filter '{filter_task}'.\n")
        return

    today_dt = date.today()
    today_str = today_dt.strftime("%Y-%m-%d")
    daily_totals = {}
    task_totals = {}
    
    for s in sessions:
        d = s["date"]
        t = s.get("task", "Deep Work")
        daily_totals[d] = daily_totals.get(d, 0) + s["focus_seconds"]
        task_totals[t] = task_totals.get(t, 0) + s["focus_seconds"]

    today_focus = daily_totals.get(today_str, 0)
    total_focus = sum(s["focus_seconds"] for s in sessions)
    goal_str = format_short_time(DAILY_GOAL_SECONDS)

    print(f"\n📅 Today ({today_str}):")
    print(f"  • Focus Logged : \033[1;32m{format_time(today_focus)}\033[0m")
    print(f"  • Daily Goal   : {render_ascii_bar(min(1.0, today_focus / DAILY_GOAL_SECONDS))} ({format_short_time(today_focus)} / {goal_str})")

    print(f"\n🗓️  28-Day Consistency Heatmap (Goal: {goal_hours:g}h/day):")
    print(f"  {render_activity_heatmap(daily_totals, DAILY_GOAL_SECONDS)}")
    print("  \033[2m[· 0h  ░ <35%  ▒ <70%  ▓ <100%  █ Goal Met]\033[0m")

    print(f"\n📈 Last 7 Days Activity:")
    print("  Date       | Focus Time  | Daily Target")
    print("  -----------+-------------+-----------------------------")
    for i in range(6, -1, -1):
        d_str = (today_dt - timedelta(days=i)).strftime("%Y-%m-%d")
        sec = daily_totals.get(d_str, 0)
        mark = " (Today)" if d_str == today_str else ""
        print(f"  {d_str} | {format_short_time(sec):<11} | {render_ascii_bar(min(1.0, sec / DAILY_GOAL_SECONDS), width=12)}{mark}")

    if not filter_task and len(task_totals) > 1:
        print("\n🏷️  Top Focus Objectives:")
        sorted_tasks = sorted(task_totals.items(), key=lambda x: x[1], reverse=True)[:5]
        for t_name, t_sec in sorted_tasks:
            pct = (t_sec / total_focus) * 100 if total_focus > 0 else 0
            print(f"  • {t_name[:22]:<22} : {format_time(t_sec):<12} ({pct:.0f}%)")

    sorted_days = sorted([datetime.strptime(d, "%Y-%m-%d").date() for d in daily_totals.keys()])
    current_streak = 0
    check_day = today_dt if today_dt in sorted_days else today_dt - timedelta(days=1)
    while check_day in sorted_days:
        current_streak += 1
        check_day -= timedelta(days=1)

    print(f"\n🏆 Summary Highlights:")
    print(f"  • Daily Target    : {goal_hours:g} hour(s)/day")
    print(f"  • Total Focus     : {format_time(total_focus)} across {len(sessions)} cycle(s)")
    print(f"  • Current Streak  : \033[1;33m{current_streak} day(s)\033[0m")
    print(f"  • Active Vault    : \033[0;36m{md_file}\033[0m\n" + "=" * 62 + "\n")
