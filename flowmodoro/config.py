import os
import json
import math

BREAK_RATIO = 0.2
DEFAULT_GOAL_HOURS = 6.0
DEFAULT_MAX_BREAK_MINS = None
USER_HOME = os.path.expanduser("~")
CONFIG_FILE = os.path.join(USER_HOME, ".flowmodoro_config.json")
DEFAULT_TARGET_DIR = os.path.join(USER_HOME, "Documents", "Flowmodoro")

def get_config():
    cfg = None
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                if isinstance(loaded, dict):
                    cfg = loaded
        except Exception:
            pass

    if cfg is None:
        cfg = {}

    target_dir = cfg.get("target_dir")
    if not isinstance(target_dir, str) or not target_dir.strip():
        cfg["target_dir"] = DEFAULT_TARGET_DIR
    else:
        cfg["target_dir"] = target_dir.strip()

    cfg.setdefault("start_sound", None)
    cfg.setdefault("stop_sound", None)

    goal = cfg.get("daily_goal_hours")
    if not isinstance(goal, (int, float)) or not math.isfinite(goal) or goal <= 0:
        cfg["daily_goal_hours"] = DEFAULT_GOAL_HOURS

    max_b = cfg.get("max_break_minutes")
    if max_b is not None:
        if not isinstance(max_b, (int, float)) or not math.isfinite(max_b) or max_b <= 0:
            cfg["max_break_minutes"] = DEFAULT_MAX_BREAK_MINS

    return cfg

def save_config(config_data):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=2)
    except Exception as e:
        print(f"\033[1;31mError saving configuration: {e}\033[0m\n")

def set_persistent_directory(raw_path):
    if not raw_path or not isinstance(raw_path, str) or "\0" in raw_path:
        print("\033[1;31mError: Invalid directory path specified.\033[0m\n")
        return

    cleaned = raw_path.strip()
    if not cleaned:
        print("\033[1;31mError: Path cannot be empty.\033[0m\n")
        return

    try:
        expanded_path = os.path.abspath(os.path.expanduser(cleaned))
        if os.path.isfile(expanded_path):
            print(f"\033[1;31mError: Path '{expanded_path}' is an existing file, not a directory.\033[0m\n")
            return

        os.makedirs(expanded_path, exist_ok=True)
        config = get_config()
        config["target_dir"] = expanded_path
        save_config(config)
        print(f"\033[1;32m✓ Persistent log path set to:\033[0m\n  📂 {expanded_path}\n")
    except Exception as e:
        print(f"\033[1;31mError setting persistent directory: {e}\033[0m\n")

def set_daily_goal(hours_str):
    if not hours_str or not isinstance(hours_str, str):
        print("\033[1;31mError: Please enter a valid number of hours (e.g. 4, 6.5, 8).\033[0m\n")
        return
    try:
        hours = float(hours_str)
        if not math.isfinite(hours) or hours <= 0:
            print("\033[1;31mError: Daily goal must be a positive number greater than 0 hours (e.g. 6.0).\033[0m\n")
            return
        if hours > 24:
            print("\033[1;31mError: Daily focus goal cannot exceed 24 hours per day.\033[0m\n")
            return

        config = get_config()
        config["daily_goal_hours"] = round(hours, 2)
        save_config(config)
        print(f"\033[1;32m✓ Daily deep work goal set to: {hours:g} hours/day\033[0m\n")
    except ValueError:
        print("\033[1;31mError: Please enter a valid number of hours (e.g. 4, 6.5, 8).\033[0m\n")

def set_max_break(minutes_str):
    if not minutes_str or not isinstance(minutes_str, str):
        print("\033[1;31mError: Please enter a valid number of minutes (e.g. 15, 20, 30).\033[0m\n")
        return
    try:
        mins = float(minutes_str)
        if not math.isfinite(mins):
            print("\033[1;31mError: Please enter a valid number of minutes (e.g. 15, 20, 30).\033[0m\n")
            return

        config = get_config()
        if mins <= 0:
            config["max_break_minutes"] = None
            save_config(config)
            print("\033[1;32m✓ Maximum break cap disabled (unlimited earned rest).\033[0m\n")
        else:
            if mins > 1440:
                print("\033[1;31mError: Maximum break duration cannot exceed 1440 minutes (24 hours).\033[0m\n")
                return
            config["max_break_minutes"] = round(mins, 1)
            save_config(config)
            print(f"\033[1;32m✓ Maximum break duration capped at: {mins:g} minutes\033[0m\n")
    except ValueError:
        print("\033[1;31mError: Please enter a valid number of minutes (e.g. 15, 20, 30).\033[0m\n")

def set_custom_sound(sound_type, file_path):
    if not file_path or not isinstance(file_path, str) or "\0" in file_path:
        print("\033[1;31mError: Invalid file path for audio sound.\033[0m\n")
        return

    cleaned = file_path.strip()
    if not cleaned:
        print("\033[1;31mError: Audio file path cannot be empty.\033[0m\n")
        return

    try:
        expanded_path = os.path.abspath(os.path.expanduser(cleaned))
        if os.path.isdir(expanded_path):
            print(f"\033[1;31mError: Path '{expanded_path}' is a directory, not an audio file.\033[0m\n")
            return
        if not os.path.exists(expanded_path):
            print(f"\033[1;31mError: File not found at '{expanded_path}'\033[0m\n")
            return

        config = get_config()
        config[sound_type] = expanded_path
        save_config(config)
        print(f"\033[1;32m✓ Custom audio saved for [{sound_type}]:\033[0m\n  🎵 {expanded_path}\n")
    except Exception as e:
        print(f"\033[1;31mError setting custom sound: {e}\033[0m\n")

def reset_sound_defaults():
    config = get_config()
    config["start_sound"] = None
    config["stop_sound"] = None
    save_config(config)
    print("\033[1;32m✓ Audio alerts reset to system default chimes.\033[0m\n")

def get_active_paths():
    config = get_config()
    target_dir = config.get("target_dir", DEFAULT_TARGET_DIR)
    try:
        os.makedirs(target_dir, exist_ok=True)
    except Exception:
        target_dir = DEFAULT_TARGET_DIR
        os.makedirs(target_dir, exist_ok=True)

    return (
        target_dir,
        os.path.join(target_dir, "flowmodoro_data.jsonl"),
        os.path.join(target_dir, "flowmodoro_log.md")
    )

