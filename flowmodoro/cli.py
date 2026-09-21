import argparse
import sys
import time
import math
from .config import (
    BREAK_RATIO,
    DEFAULT_POMODORO_MINS,
    POMODORO_CYCLE_COUNT,
    calculate_pomodoro_break,
    set_default_pomodoro,
    set_persistent_directory,
    set_daily_goal,
    set_max_break,
    set_day_cutoff,
    set_theme,
    set_custom_sound,
    reset_sound_defaults,
    set_alarm_repeat,
    set_cue_repeat,
    get_active_paths,
    get_config,
    THEME_PALETTES,
    DEFAULT_THEME
)
from .storage import (
    save_session,
    delete_last_session,
    interactive_delete_session,
    delete_by_task,
    delete_all_sessions,
    export_data,
    format_time,
    format_short_time,
    normalize_task_name
)
from .dashboard import display_dashboard
from .timers import run_focus_session, run_break_session, run_pomodoro_session
from .audio import interactive_system_sound_picker

class FormattedParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        kwargs["allow_abbrev"] = False
        super().__init__(*args, **kwargs)

    def format_help(self):
        return """\
\033[1;36m======================================================================\033[0m
\033[1;37m                 ⚡ FLOWMODORO CLI HELP & COMMANDS ⚡\033[0m
\033[1;36m======================================================================\033[0m

\033[1;33mUSAGE:\033[0m
  flowmodoro [OPTIONS]

\033[1;33mCORE COMMANDS:\033[0m
  flowmodoro                     Start an interactive focus & flow session
  flowmodoro -P, --pomodoro [M]  Start a Pomodoro countdown session (default: 25m)
  flowmodoro -t, --task <NAME>   Start session directly with designated task name
  flowmodoro -s, --stats         Display analytics dashboard & 28-day heatmap
  flowmodoro -s -t <TOPIC>       Display analytics filtered by a specific task/tag

\033[1;33mGOALS, THEMES & STORAGE:\033[0m
  flowmodoro --set-pomodoro <M>  Set default Pomodoro focus duration in minutes
  flowmodoro -g, --goal <HOURS>  Set daily focus goal in hours (default: 4h)
  flowmodoro --theme <COLOR>     Set heatmap theme (green, red, blue, orange, purple)
  flowmodoro --max-break <MINS>  Cap maximum break duration (e.g. 20; 0 to uncap)
  flowmodoro --cutoff <HOUR>     Set day cutoff hour for night owls (e.g. 3 for 3 AM)
  flowmodoro -p, --path <DIR>    Set persistent folder for Markdown & JSONL data
  flowmodoro -w, --where         Show current storage paths, audio settings & goal
  flowmodoro -e, --export <FILE> Export session logs to CSV, JSON, or XLSX format

\033[1;33mAUDIO CONFIGURATION:\033[0m
  flowmodoro --sounds            Interactive browser to preview & select OS native sounds
  flowmodoro --sound-focus <F>   Set custom audio for starting a focus session
  flowmodoro --sound-start <F>   Set custom audio for break start (.mp3, .m4a, .wav)
  flowmodoro --sound-stop <F>    Set custom audio for break completion alarm
  flowmodoro --repeat-focus <M>  Toggle repeating loop for Focus Start (on / off)
  flowmodoro --repeat-start <M>  Toggle repeating loop for Break Start (on / off)
  flowmodoro --repeat-stop <M>  Toggle repeating loop for Break End Alarm (on / off)
  flowmodoro --sound-default     Reset all sound cues back to OS system defaults

\033[1;33mSESSION PRUNING & HISTORY:\033[0m
  flowmodoro -u, --undo          Remove the most recently recorded session
  flowmodoro -d, --delete        Interactive mass deletion (range '1-5', list '1,3', 'all', or task)
  flowmodoro --delete-task <T>   Mass delete all sessions matching task name <T>
  flowmodoro --clear-all         Permanently purge all recorded session logs

\033[1;33mHELP:\033[0m
  flowmodoro -h, --help          Show this command reference
\033[1;36m======================================================================\033[0m
"""

    def parse_args(self, args=None, namespace=None):
        raw_args = sys.argv[1:] if args is None else list(args)
        known_long_options = {
            "pomodoro": ("--pomodoro", "-P"),
            "set-pomodoro": ("--set-pomodoro", None),
            "delete": ("--delete", "-d"),
            "delete-task": ("--delete-task", None),
            "delete-all": ("--delete-all", None),
            "clear-all": ("--clear-all", None),
            "stats": ("--stats", "-s"),
            "goal": ("--goal", "-g"),
            "theme": ("--theme", None),
            "color-scheme": ("--color-scheme", None),
            "cutoff": ("--cutoff", None),
            "day-cutoff": ("--day-cutoff", None),
            "path": ("--path", "-p"),
            "export": ("--export", "-e"),
            "sounds": ("--sounds", None),
            "sound-focus": ("--sound-focus", None),
            "sound-start": ("--sound-start", None),
            "sound-stop": ("--sound-stop", None),
            "sound-default": ("--sound-default", None),
            "alarm-repeat": ("--alarm-repeat", None),
            "repeat-alarm": ("--repeat-alarm", None),
            "no-repeat-alarm": ("--no-repeat-alarm", None),
            "repeat-focus": ("--repeat-focus", None),
            "repeat-start": ("--repeat-start", None),
            "repeat-stop": ("--repeat-stop", None),
            "max-break": ("--max-break", None),
            "where": ("--where", "-w"),
            "task": ("--task", "-t"),
            "undo": ("--undo", "-u"),
            "help": ("--help", "-h"),
        }
        for a in raw_args:
            if a.startswith("-") and not a.startswith("--") and len(a) > 2:
                name = a[1:].split("=")[0]
                if name in known_long_options:
                    long_opt, short_opt = known_long_options[name]
                    hint = f"Did you mean '{long_opt}'" + (f" or '{short_opt}'?" if short_opt else "?")
                    self.error(f"unrecognized option '{a}'. {hint}")
                else:
                    self.error(f"unrecognized option '{a}'.")

        return super().parse_args(args=args, namespace=namespace)


def prompt_break_choice():
    """Prompt for earned break action, rejecting any input other than Y, N, C, Q."""
    while True:
        try:
            val = input("\nStart earned break now? [Y/n/c/q]: ").strip().lower()
            if not val or val in ('y', 'yes'):
                return 'y'
            elif val in ('n', 'no'):
                return 'n'
            elif val in ('c', 'cancel'):
                return 'c'
            elif val in ('q', 'quit', 'exit'):
                return 'q'
            print("\033[1;31mInvalid option. Please enter 'y' (yes), 'n' (no), 'c' (cancel), or 'q' (quit).\033[0m")
        except (KeyboardInterrupt, EOFError):
            raise

def prompt_next_session_choice(task):
    """Prompt before starting a new focus session, rejecting invalid inputs."""
    while True:
        try:
            val = input(f"\nStart another focus session on '\033[1;36m{task}\033[0m'? [Y/n/q]: ").strip().lower()
            if not val or val in ('y', 'yes'):
                return 'y'
            elif val in ('n', 'no'):
                return 'n'
            elif val in ('q', 'quit', 'exit'):
                return 'q'
            print("\033[1;31mInvalid option. Please enter 'y' (yes), 'n' (no), or 'q' (quit).\033[0m")
        except (KeyboardInterrupt, EOFError):
            raise

def prompt_short_session_retry():
    """Prompt when focus duration is < 1s, rejecting invalid inputs."""
    while True:
        try:
            val = input("Start another session? [Y/n]: ").strip().lower()
            if not val or val in ('y', 'yes'):
                return 'y'
            elif val in ('n', 'no'):
                return 'n'
            print("\033[1;31mInvalid option. Please enter 'y' (yes) or 'n' (no).\033[0m")
        except (KeyboardInterrupt, EOFError):
            raise


def prompt_mode_choice():
    """Prompt to choose mode: [1] Flowmodoro (open stopwatch), [2] Pomodoro (countdown timer)."""
    while True:
        try:
            val = input("\nSelect Focus Mode:\n  [1] ⚡ Flowmodoro (uninterrupted stopwatch flow)\n  [2] 🍅 Pomodoro   (custom countdown timer)\nChoose [1/2, default: 1]: ").strip().lower()
            if not val or val in ('1', 'flow', 'flowmodoro', 'f'):
                return 'flow'
            elif val in ('2', 'pomo', 'pomodoro', 'p'):
                return 'pomodoro'
            print("\033[1;31mInvalid choice. Enter '1' for Flowmodoro or '2' for Pomodoro.\033[0m")
        except (KeyboardInterrupt, EOFError):
            raise

def prompt_pomodoro_minutes(default_mins=25):
    """Prompt user to choose how many minutes for the Pomodoro session."""
    while True:
        try:
            val = input(f"Enter Pomodoro focus duration in minutes [default: {default_mins:g}]: ").strip()
            if not val:
                return float(default_mins)
            mins = float(val)
            if math.isfinite(mins) and mins > 0:
                return mins
            print("\033[1;31mPlease enter a valid positive number of minutes.\033[0m")
        except (KeyboardInterrupt, EOFError):
            raise
        except ValueError:
            print("\033[1;31mInvalid number. Please enter a valid number of minutes.\033[0m")

def parse_pomodoro_minutes_arg(val_str, default_mins=25):
    """Validate minutes passed via CLI flag."""
    if not val_str or val_str == "DEFAULT":
        return float(default_mins)
    try:
        val = float(val_str)
        if math.isfinite(val) and val > 0:
            return val
        print(f"\033[1;31mError: Pomodoro duration must be greater than 0. Received '{val_str}'.\033[0m\n")
        sys.exit(1)
    except ValueError:
        print(f"\033[1;31mError: Invalid Pomodoro duration '{val_str}'. Please provide a valid number of minutes.\033[0m\n")
        sys.exit(1)

def prompt_next_pomodoro_choice(task, cycle, total_cycles):
    while True:
        try:
            val = input(f"\nStart next Pomodoro [Cycle {cycle}/{total_cycles}] on '\033[1;36m{task}\033[0m'? [Y/n/q]: ").strip().lower()
            if not val or val in ('y', 'yes'):
                return 'y'
            elif val in ('n', 'no'):
                return 'n'
            elif val in ('q', 'quit', 'exit'):
                return 'q'
            print("\033[1;31mInvalid option. Please enter 'y' (yes), 'n' (no), or 'q' (quit).\033[0m")
        except (KeyboardInterrupt, EOFError):
            raise

def run_pomodoro_loop(task, focus_mins):
    total_day_focus = 0
    cycle = 1
    _, _, md_file = get_active_paths()

    short_break_sec, _ = calculate_pomodoro_break(focus_mins, cycle_index=1)
    long_break_sec, _ = calculate_pomodoro_break(focus_mins, cycle_index=POMODORO_CYCLE_COUNT)

    print(f"\n🍅 \033[1;32mPomodoro Configured:\033[0m {focus_mins:g}m Focus ➔ {format_short_time(short_break_sec)} Short Break ({format_short_time(long_break_sec)} Long Break every {POMODORO_CYCLE_COUNT} pomodoros)")
    time.sleep(1)

    while True:
        try:
            elapsed_sec, start_dt, end_dt, completed_full = run_pomodoro_session(
                target_minutes=focus_mins,
                task_name=task,
                cycle=cycle,
                total_cycles=POMODORO_CYCLE_COUNT
            )
        except (KeyboardInterrupt, EOFError):
            print("\nSession ended. Great work today!")
            break

        if elapsed_sec < 1.0:
            print("\nFocus session too short (< 1s), session not logged.")
            try:
                retry = prompt_short_session_retry()
                if retry == 'n':
                    print("Session ended. Great work today!")
                    break
                continue
            except (KeyboardInterrupt, EOFError):
                print("\nSession ended. Great work today!")
                break

        total_day_focus += elapsed_sec

        if completed_full:
            earned_break, is_long_break = calculate_pomodoro_break(focus_mins, cycle_index=cycle)
            break_label = f"Long Break (Cycle {cycle}/{POMODORO_CYCLE_COUNT})" if is_long_break else f"Short Break (Cycle {cycle}/{POMODORO_CYCLE_COUNT})"
        else:
            earned_break = elapsed_sec * BREAK_RATIO
            is_long_break = False
            break_label = "Partial Rest (Paused Early)"

        save_session(start_dt, end_dt, elapsed_sec, earned_break, task_name=task)
        print(f"\nCompleted Focus:   {format_short_time(elapsed_sec)}")
        print(f"Earned Recovery:   {format_short_time(earned_break)} [{break_label}]")
        print(f"Total Today:       {format_time(total_day_focus)}")
        print(f"\033[0;32m✓ Saved to {md_file}\033[0m")

        if completed_full and is_long_break:
            print("\n\033[1;35m🎉 4-Pomodoro Set Complete! You earned a well-deserved long break.\033[0m")

        try:
            break_choice = prompt_break_choice()
        except (KeyboardInterrupt, EOFError):
            print("\nSession ended. Great work today!")
            break

        if break_choice == 'q':
            print("Session ended. Great work today!")
            break
        elif break_choice == 'y':
            title = f"🍅 POMODORO: {break_label.upper()}"
            run_break_session(earned_break, title=title)

        if completed_full:
            cycle = 1 if is_long_break else cycle + 1

        try:
            next_choice = prompt_next_pomodoro_choice(task, cycle, POMODORO_CYCLE_COUNT)
        except (KeyboardInterrupt, EOFError):
            print("\nSession ended. Great work today!")
            break

        if next_choice in ('n', 'q'):
            print("Session ended. Great work today!")
            break

def main():
    parser = FormattedParser(description="Flowmodoro CLI & Deep Work Tracker", allow_abbrev=False)

    parser.add_argument("--pomodoro", "-P", nargs="?", const="DEFAULT", type=str, help="Start a Pomodoro countdown session (e.g. -P 25)")
    parser.add_argument("--set-pomodoro", type=str, help="Set default Pomodoro focus duration in minutes")
    parser.add_argument("--goal", "-g", type=str, help="Set daily focus goal in hours")
    parser.add_argument("--theme", "--color-scheme", type=str, help="Set heatmap theme (green, red, blue, orange, purple)")
    parser.add_argument("--max-break", type=str, help="Cap maximum break duration in minutes")
    parser.add_argument("--cutoff", "--day-cutoff", type=str, help="Set day cutoff hour for night owls (e.g. 3 for 3 AM)")
    parser.add_argument("--path", "-p", type=str, help="Set persistent storage folder")
    parser.add_argument("--export", "-e", type=str, help="Export logs to CSV, JSON, or XLSX")
    parser.add_argument("--sound-focus", type=str, help="Set custom focus session start chime")
    parser.add_argument("--sound-start", type=str, help="Set custom break start sound")
    parser.add_argument("--sound-stop", type=str, help="Set custom break complete alarm")
    parser.add_argument("--alarm-repeat", type=str, help="Toggle break alarm repeat loop (on/off)")
    parser.add_argument("--repeat-alarm", action="store_true", help="Enable break alarm repeat loop")
    parser.add_argument("--no-repeat-alarm", action="store_true", help="Disable break alarm repeat loop")
    parser.add_argument("--repeat-focus", type=str, help="Toggle repeat loop for Focus Start (on/off)")
    parser.add_argument("--repeat-start", type=str, help="Toggle repeat loop for Break Start (on/off)")
    parser.add_argument("--repeat-stop", type=str, help="Toggle repeat loop for Break End Alarm (on/off)")
    parser.add_argument("--sound-default", action="store_true", help="Reset sounds to default")
    parser.add_argument("--sounds", action="store_true", help="Browse native system sounds")
    parser.add_argument("--where", "-w", action="store_true", help="Show active config")
    parser.add_argument("--stats", "-s", action="store_true", help="Show stats dashboard")
    parser.add_argument("--task", "-t", type=str, help="Session task name or filter tag")
    parser.add_argument("--undo", "-u", action="store_true", help="Undo last session")
    parser.add_argument("--delete", "-d", action="store_true", help="Interactive deletion")
    parser.add_argument("--delete-task", type=str, help="Mass delete sessions matching task name")
    parser.add_argument("--clear-all", "--delete-all", action="store_true", help="Clear all session history")
    args = parser.parse_args()

    if args.set_pomodoro:
        set_default_pomodoro(args.set_pomodoro)
        return
    if args.goal:
        set_daily_goal(args.goal)
        return
    if args.theme:
        set_theme(args.theme)
        return
    if args.max_break is not None:
        set_max_break(args.max_break)
        return
    if args.cutoff is not None:
        set_day_cutoff(args.cutoff)
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
    if args.repeat_focus:
        set_cue_repeat("focus_sound", args.repeat_focus)
        return
    if args.repeat_start:
        set_cue_repeat("start_sound", args.repeat_start)
        return
    if args.repeat_stop:
        set_cue_repeat("stop_sound", args.repeat_stop)
        return
    if args.alarm_repeat:
        set_alarm_repeat(args.alarm_repeat)
        return
    if args.repeat_alarm:
        set_alarm_repeat("on")
        return
    if args.no_repeat_alarm:
        set_alarm_repeat("off")
        return
    if args.sound_focus:
        set_custom_sound("focus_sound", args.sound_focus)
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
        cutoff_val = cfg.get("day_cutoff_hour", 0)
        cutoff_str = f"{cutoff_val}:00 AM (Night Owl Mode)" if cutoff_val > 0 else "00:00 Midnight (Default)"
        t_name = cfg.get("theme", DEFAULT_THEME)
        t_info = THEME_PALETTES.get(t_name, THEME_PALETTES[DEFAULT_THEME])
        f_rep = " \033[0;32m[Loop]\033[0m" if cfg.get("repeat_focus_sound", False) else " \033[0;33m[Single Chime]\033[0m"
        b_rep = " \033[0;32m[Loop]\033[0m" if cfg.get("repeat_start_sound", False) else " \033[0;33m[Single Chime]\033[0m"
        a_rep = " \033[0;32m[Loop]\033[0m" if cfg.get("repeat_stop_sound", True) else " \033[0;33m[Single Chime]\033[0m"
        p_mins = cfg.get("default_pomodoro_minutes", DEFAULT_POMODORO_MINS)
        p_short, _ = calculate_pomodoro_break(p_mins, 1)
        p_long, _ = calculate_pomodoro_break(p_mins, POMODORO_CYCLE_COUNT)

        print(f"\n📂 Active Storage Directory: \033[1;36m{target_dir}\033[0m")
        print(f"🎯 Daily Focus Goal       : \033[1;33m{cfg.get('daily_goal_hours', 4.0):g} hours/day\033[0m")
        print(f"🍅 Default Pomodoro       : \033[1;32m{p_mins:g} mins\033[0m (Break: {p_short/60:g}m short / {p_long/60:g}m long)")
        print(f"🎨 Heatmap Color Theme   : \033[1;35m{t_info['emoji']} {t_info['name']}\033[0m")
        print(f"⏱️  Max Break Limit        : \033[0;33m{max_b}\033[0m")
        print(f"🌙 Day Cutoff Hour        : \033[0;33m{cutoff_str}\033[0m")
        print(f"📄 Markdown Journal       : \033[0;32m{md_file}\033[0m")
        print(f"💾 JSONL Data Store       : \033[0;32m{data_file}\033[0m")
        print(f"🎵 Focus Start Audio      : \033[0;33m{cfg.get('focus_sound') or 'System Default'}\033[0m{f_rep}")
        print(f"🔔 Break Start Audio      : \033[0;33m{cfg.get('start_sound') or 'System Default'}\033[0m{b_rep}")
        print(f"⏰ Break End Alarm Audio  : \033[0;33m{cfg.get('stop_sound') or 'System Default'}\033[0m{a_rep}\n")
        return

    if args.stats:
        display_dashboard(filter_task=args.task)
        return
    if args.delete_task:
        delete_by_task(normalize_task_name(args.delete_task))
        return
    if args.clear_all:
        delete_all_sessions()
        return
    if args.undo:
        delete_last_session()
        return
    if args.delete:
        interactive_delete_session()
        return

    cfg = get_config()
    default_pomo_mins = cfg.get("default_pomodoro_minutes", DEFAULT_POMODORO_MINS)

    if args.task:
        task = normalize_task_name(args.task)
    else:
        try:
            prompt = input("Enter focus task/topic (Press Enter for 'DEEP_WORK'): ").strip()
            task = normalize_task_name(prompt) if prompt else "DEEP_WORK"
        except (KeyboardInterrupt, EOFError):
            print("\nSession canceled.")
            return

    # Determine mode: Flowmodoro or Pomodoro
    if args.pomodoro is not None:
        mode = 'pomodoro'
        if args.pomodoro == "DEFAULT":
            try:
                pomo_mins = prompt_pomodoro_minutes(default_pomo_mins)
            except (KeyboardInterrupt, EOFError):
                print("\nSession canceled.")
                return
        else:
            pomo_mins = parse_pomodoro_minutes_arg(args.pomodoro, default_pomo_mins)
    else:
        try:
            mode = prompt_mode_choice()
            if mode == 'pomodoro':
                pomo_mins = prompt_pomodoro_minutes(default_pomo_mins)
        except (KeyboardInterrupt, EOFError):
            print("\nSession canceled.")
            return

    if mode == 'pomodoro':
        run_pomodoro_loop(task, pomo_mins)
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
                retry = prompt_short_session_retry()
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
            break_choice = prompt_break_choice()
        except (KeyboardInterrupt, EOFError):
            print("\nSession ended. Great work today!")
            break

        if break_choice == 'q':
            print("Session ended. Great work today!")
            break
        elif break_choice == 'y':
            run_break_session(earned_break)

        try:
            next_choice = prompt_next_session_choice(task)
        except (KeyboardInterrupt, EOFError):
            print("\nSession ended. Great work today!")
            break

        if next_choice in ('n', 'q'):
            print("Session ended. Great work today!")
            break


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nGoodbye!")
        sys.exit(0)
