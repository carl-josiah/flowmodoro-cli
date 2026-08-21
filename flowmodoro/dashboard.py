import os
from datetime import date, timedelta, datetime
from .config import get_active_paths
from .storage import load_all_sessions, format_time, format_short_time

def render_ascii_bar(progress, width=20):
    filled = int(round(progress * width))
    filled = min(width, max(0, filled))
    return f"[{'█' * filled}{'░' * (width - filled)}] {int(progress * 100)}%"

def display_dashboard():
    target_dir, _, md_file = get_active_paths()
    sessions = load_all_sessions()
    os.system('cls' if os.name == 'nt' else 'clear')
    print("=" * 60 + "\n             ⚡ FLOWMODORO ANALYTICS DASHBOARD ⚡\n" + "=" * 60)

    if not sessions:
        print(f"\nNo recorded sessions found yet.\n📂 Active Path: \033[0;36m{target_dir}\033[0m\n")
        return

    today_dt = date.today()
    today_str = today_dt.strftime("%Y-%m-%d")
    daily_totals = {}
    for s in sessions:
        daily_totals[s["date"]] = daily_totals.get(s["date"], 0) + s["focus_seconds"]

    today_focus = daily_totals.get(today_str, 0)
    DAILY_GOAL_SECONDS = 6 * 3600

    print(f"\n📅 Today ({today_str}):\n  • Focus Logged : \033[1;32m{format_time(today_focus)}\033[0m")
    print(f"  • Daily 6h Goal: {render_ascii_bar(min(1.0, today_focus / DAILY_GOAL_SECONDS))} ({format_short_time(today_focus)} / 06:00:00)")

    print("\n📈 Last 7 Days Activity:\n  Date       | Focus Time  | Daily 6h Target\n  -----------+-------------+-----------------------------")
    for i in range(6, -1, -1):
        d_str = (today_dt - timedelta(days=i)).strftime("%Y-%m-%d")
        sec = daily_totals.get(d_str, 0)
        mark = " (Today)" if d_str == today_str else ""
        print(f"  {d_str} | {format_short_time(sec):<11} | {render_ascii_bar(min(1.0, sec / DAILY_GOAL_SECONDS), width=12)}{mark}")

    sorted_days = sorted([datetime.strptime(d, "%Y-%m-%d").date() for d in daily_totals.keys()])
    current_streak = 0
    check_day = today_dt if today_dt in sorted_days else today_dt - timedelta(days=1)
    while check_day in sorted_days:
        current_streak += 1
        check_day -= timedelta(days=1)

    print(f"\n🏆 Summary Highlights:\n  • Total Sessions  : {len(sessions)}")
    print(f"  • Lifetime Focus  : {format_time(sum(s['focus_seconds'] for s in sessions))}")
    print(f"  • Current Streak  : \033[1;33m{current_streak} day(s)\033[0m")
    print(f"  • Active Directory: \033[0;36m{target_dir}\033[0m\n  • Markdown Vault  : \033[0;36m{md_file}\033[0m\n" + "=" * 60 + "\n")
