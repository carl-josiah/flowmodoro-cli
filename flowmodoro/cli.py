import argparse
import sys
from .config import (
    BREAK_RATIO,
    set_persistent_directory,
    set_custom_sound,
    reset_sound_defaults,
    get_active_paths,
    get_config,
)
from .storage import (
    save_session,
    delete_last_session,
    interactive_delete_session,
    format_time,
    format_short_time,
)
from .dashboard import display_dashboard
from .timers import run_focus_session, run_break_session


class FormattedParser(argparse.ArgumentParser):
    """Custom parser providing clean terminal formatting for --help."""

    def format_help(self):
        return """\
\033[1;36m============================================================\033[0m
\033[1;37m             ⚡ FLOWMODORO CLI HELP & COMMANDS ⚡\033[0m
\033[1;36m============================================================\033[0m

\033[1;33mUSAGE:\033[0m
  flowmodoro [OPTIONS]

\033[1;33mCORE COMMANDS:\033[0m
  flowmodoro                     Start an interactive focus & flow session
  flowmodoro -t, --task <NAME>   Start directly with a designated task name
  flowmodoro -s, --stats         Display the 7-day deep work analytics dashboard

\033[1;33mPATH & STORAGE CONFIGURATION:\033[0m
  flowmodoro -p, --path <DIR>    Set persistent folder for Markdown & data storage
  flowmodoro -w, --where         Show current storage paths and audio settings

\033[1;33mCUSTOM AUDIO ALARMS:\033[0m
  flowmodoro --sound-start <FILE>  Set custom audio for break start (.mp3, .m4a, .wav)
  flowmodoro --sound-stop <FILE>   Set custom audio for break completion alarm
  flowmodoro --sound-default       Reset all sound cues back to OS system defaults

\033[1;33mSESSION PRUNING & HISTORY:\033[0m
  flowmodoro -u, --undo          Remove the most recently recorded session
  flowmodoro -d, --delete        Interactively browse and delete specific logs

\033[1;33mHELP:\033[0m
  flowmodoro -h, --help          Show this command reference
\033[1;36m============================================================\033[0m
"""


def main():
    parser = FormattedParser(description="Flowmodoro CLI & Deep Work Tracker")
    parser.add_argument("--path", "-p", type=str)
    parser.add_argument("--sound-start", type=str)
    parser.add_argument("--sound-stop", type=str)
    parser.add_argument("--sound-default", action="store_true")
    parser.add_argument("--where", "-w", action="store_true")
    parser.add_argument("--stats", "-s", action="store_true")
    parser.add_argument("--task", "-t", type=str, default="Deep Work")
    parser.add_argument("--undo", "-u", action="store_true")
    parser.add_argument("--delete", "-d", action="store_true")
    parser.add_argument(
        "--sounds",
        action="store_true",
        help="Browse, preview, and select native system sounds",
    )

    args = parser.parse_args()

    if args.path:
        set_persistent_directory(args.path)
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
        print(f"\n📂 Active Storage Directory: \033[1;36m{target_dir}\033[0m")
        print(f"📄 Markdown Journal       : \033[0;32m{md_file}\033[0m")
        print(f"💾 JSONL Data Store       : \033[0;32m{data_file}\033[0m")
        print(
            f"🔔 Break Start Audio      : \033[0;33m{cfg.get('start_sound') or 'System Default'}\033[0m"
        )
        print(
            f"⏰ Break End Alarm Audio  : \033[0;33m{cfg.get('stop_sound') or 'System Default'}\033[0m\n"
        )
        return
    if args.stats:
        display_dashboard()
        return
    if args.undo:
        delete_last_session()
        return
    if args.delete:
        interactive_delete_session()
        return
    from .audio import interactive_system_sound_picker

    if args.sounds:
        interactive_system_sound_picker()
        return

    # Start session
    task = args.task
    if task == "Deep Work":
        prompt = input("Enter focus task/topic (Press Enter for 'Deep Work'): ").strip()
        if prompt:
            task = prompt

    total_day_focus = 0
    _, _, md_file = get_active_paths()
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
        if choice == "q":
            print("Session ended. Great work today!")
            break
        elif choice != "n":
            run_break_session(earned_break)


if __name__ == "__main__":
    main()
