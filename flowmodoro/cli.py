import argparse
import sys
from .config import (
    BREAK_RATIO,
    set_persistent_directory,
    set_daily_goal,
    set_max_break,
    set_custom_sound,
    reset_sound_defaults,
    get_active_paths,
    get_config
)
from .storage import (
    save_session,
    delete_last_session,
    interactive_delete_session,
    export_data,
    format_time,
    format_short_time
)
from .dashboard import display_dashboard
from .timers import run_focus_session, run_break_session
from .audio import interactive_system_sound_picker

class FormattedParser(argparse.ArgumentParser):
    def format_help(self):
        return """\
\033[1;36m======================================================================\033[0m
\033[1;37m                 ⚡ FLOWMODORO CLI HELP & COMMANDS ⚡\033[0m
\033[1;36m======================================================================\033[0m

\033[1;33mUSAGE:\033[0m
  flowmodoro [OPTIONS]

\033[1;33mCORE COMMANDS:\033[0m
  flowmodoro                     Start an interactive focus & flow session
  flowmodoro -t, --task <NAME>   Start session directly with designated task name
  flowmodoro -s, --stats         Display analytics dashboard & 28-day heatmap
  flowmodoro -s -t <TOPIC>       Display analytics filtered by a specific task/tag

\033[1;33mGOALS, LIMITS & STORAGE:\033[0m
  flowmodoro -g, --goal <HOURS>  Set daily focus goal in hours (default: 6h)
  flowmodoro --max-break <MINS>  Cap maximum break duration (e.g. 20; 0 to uncap)
  flowmodoro -p, --path <DIR>    Set persistent folder for Markdown & JSONL data
  flowmodoro -w, --where         Show current storage paths, audio settings & goal
  flowmodoro -e, --export <FILE> Export session logs to CSV or JSON format

\033[1;33mAUDIO CONFIGURATION:\033[0m
  flowmodoro --sounds            Interactive browser to preview & select OS native sounds
  flowmodoro --sound-start <F>   Set custom audio for break start (.mp3, .m4a, .wav)
  flowmodoro --sound-stop <F>    Set custom audio for break completion alarm
  flowmodoro --sound-default     Reset all sound cues back to OS system defaults

\033[1;33mSESSION PRUNING & HISTORY:\033[0m
  flowmodoro -u, --undo          Remove the most recently recorded session
  flowmodoro -d, --delete        Interactively browse and delete specific logs

\033[1;33mHELP:\033[0m
  flowmodoro -h, --help          Show this command reference
\033[1;36m======================================================================\033[0m
"""

def main():
    parser = FormattedParser(description="Flowmodoro CLI & Deep Work Tracker")
    parser.add_argument("--goal", "-g", type=str, help="Set daily focus goal in hours")
    parser.add_argument("--max-break", type=str, help="Cap maximum break duration in minutes")
    parser.add_argument("--path", "-p", type=str, help="Set persistent storage folder")
    parser.add_argument("--export", "-e", type=str, help="Export logs to CSV or JSON")
    parser.add_argument("--sound-start", type=str, help="Set custom break start sound")
    parser.add_argument("--sound-stop", type=str, help="Set custom break complete alarm")
    parser.add_argument("--sound-default", action="store_true", help="Reset sounds to default")
    parser.add_argument("--sounds", action="store_true", help="Browse native system sounds")
    parser.add_argument("--where", "-w", action="store_true", help="Show active config")
    parser.add_argument("--stats", "-s", action="store_true", help="Show stats dashboard")
    parser.add_argument("--task", "-t", type=str, help="Session task name or filter tag")
    parser.add_argument("--undo", "-u", action="store_true", help="Undo last session")
    parser.add_argument("--delete", "-d", action="store_true", help="Interactive deletion")
    args = parser.parse_args()

    if args.goal:
        set_daily_goal(args.goal)
        return
    if args.max_break is not None:
        set_max_break(args.max_break)
        return
    if args.path:
        set_persistent_directory(args.path)
        return
    if args.export:
        export_data(args.export)
        return
    if args.sounds:
        interactive_system_sound_picker()
        return
    if args.sound_start:
        set_custom_sound("start_sound", args.sound_start)
        return
    if args.sound_stop:
        set_custom_sound("stop_sound", args.sound_stop)
        return
    if args.sound_default:
        reset_sound_defaults()
        return
    if args.where:
        target_dir, data_file, md_file = get_active_paths()
        cfg = get_config()
        max_b = f"{cfg.get('max_break_minutes'):g} min" if cfg.get("max_break_minutes") else "Disabled (Uncapped)"
        print(f"\n📂 Active Storage Directory: \033[1;36m{target_dir}\033[0m")
        print(f"🎯 Daily Focus Goal       : \033[1;33m{cfg.get('daily_goal_hours', 6.0):g} hours/day\033[0m")
        print(f"⏱️  Max Break Limit        : \033[0;33m{max_b}\033[0m")
        print(f"📄 Markdown Journal       : \033[0;32m{md_file}\033[0m")
        print(f"💾 JSONL Data Store       : \033[0;32m{data_file}\033[0m")
        print(f"🔔 Break Start Audio      : \033[0;33m{cfg.get('start_sound') or 'System Default'}\033[0m")
        print(f"⏰ Break End Alarm Audio  : \033[0;33m{cfg.get('stop_sound') or 'System Default'}\033[0m\n")
        return
    if args.stats:
        display_dashboard(filter_task=args.task)
        return
    if args.undo:
        delete_last_session()
        return
    if args.delete:
        interactive_delete_session()
        return

    task = args.task or "Deep Work"
    if not args.task:
        try:
            prompt = input("Enter focus task/topic (Press Enter for 'Deep Work'): ").strip()
            if prompt:
                task = prompt
        except (KeyboardInterrupt, EOFError):
            print("\nSession canceled.")
            return

    total_day_focus = 0
    _, _, md_file = get_active_paths()
    while True:
        try:
            focus_seconds, start_dt, end_dt = run_focus_session(task_name=task)
        except (KeyboardInterrupt, EOFError):
            print("\nSession ended. Great work today!")
            break

        if focus_seconds < 1.0:
            print("\nFocus session too short (< 1s), session not logged.")
            try:
                retry = input("Start another session? [Y/n]: ").strip().lower()
                if retry == 'n':
                    print("Session ended. Great work today!")
                    break
                continue
            except (KeyboardInterrupt, EOFError):
                print("\nSession ended. Great work today!")
                break

        total_day_focus += focus_seconds
        earned_break = focus_seconds * BREAK_RATIO

        save_session(start_dt, end_dt, focus_seconds, earned_break, task_name=task)
        print(f"Completed Focus:   {format_short_time(focus_seconds)}")
        print(f"Earned Recovery:   {format_short_time(earned_break)}")
        print(f"Total Today:       {format_time(total_day_focus)}")
        print(f"\033[0;32m✓ Saved to {md_file}\033[0m")

        try:
            choice = input("\nStart earned break now? [Y/n/q]: ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            print("\nSession ended. Great work today!")
            break

        if choice == 'q':
            print("Session ended. Great work today!")
            break
        elif choice != 'n':
            run_break_session(earned_break)

if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nGoodbye!")
        sys.exit(0)

