import os
import json
import math

from datetime import datetime, timedelta

BREAK_RATIO = 0.2
DEFAULT_GOAL_HOURS = 4.0
DEFAULT_MAX_BREAK_MINS = None
DEFAULT_DAY_CUTOFF_HOUR = 0
USER_HOME = os.path.expanduser("~")
CONFIG_FILE = os.path.join(USER_HOME, ".flowmodoro_config.json")
DEFAULT_TARGET_DIR = os.path.join(USER_HOME, "Documents", "Second Brain", "2 - Source Material", "Flowmodoro")

DEFAULT_THEME = "green"

THEME_PALETTES = {
    "green": {
        "name": "Emerald Green (GitHub Classic)",
        "emoji": "🟢",
        "levels": [
            "\033[38;5;238m■\033[0m",  # L0: 0h (Dark Gray)
            "\033[38;5;22m■\033[0m",   # L1: <35% (Dark Emerald)
            "\033[38;5;35m■\033[0m",   # L2: <70% (Medium Green)
            "\033[38;5;40m■\033[0m",   # L3: <100% (Vibrant Green)
            "\033[1;38;5;46m■\033[0m"  # L4: Goal Met (Neon Emerald)
        ]
    },
    "red": {
        "name": "Crimson Ruby",
        "emoji": "🔴",
        "levels": [
            "\033[38;5;238m■\033[0m",  # L0: 0h (Dark Gray)
            "\033[38;5;52m■\033[0m",   # L1: <35% (Dark Maroon)
            "\033[38;5;124m■\033[0m",  # L2: <70% (Ruby Red)
            "\033[38;5;160m■\033[0m",  # L3: <100% (Bright Red)
            "\033[1;38;5;196m■\033[0m" # L4: Goal Met (Neon Crimson)
        ]
    },
    "blue": {
        "name": "Sapphire Ocean",
        "emoji": "🔵",
        "levels": [
            "\033[38;5;238m■\033[0m",  # L0: 0h (Dark Gray)
            "\033[38;5;18m■\033[0m",   # L1: <35% (Dark Navy)
            "\033[38;5;26m■\033[0m",   # L2: <70% (Ocean Blue)
            "\033[38;5;33m■\033[0m",   # L3: <100% (Sky Blue)
            "\033[1;38;5;45m■\033[0m"  # L4: Goal Met (Electric Blue)
        ]
    },
    "orange": {
        "name": "Amber Sunset",
        "emoji": "🟠",
        "levels": [
            "\033[38;5;238m■\033[0m",  # L0: 0h (Dark Gray)
            "\033[38;5;94m■\033[0m",   # L1: <35% (Dark Amber)
            "\033[38;5;166m■\033[0m",  # L2: <70% (Warm Orange)
            "\033[38;5;208m■\033[0m",  # L3: <100% (Bright Orange)
            "\033[1;38;5;214m■\033[0m" # L4: Goal Met (Neon Sunset)
        ]
    },
    "purple": {
        "name": "Amethyst Violet",
        "emoji": "🟣",
        "levels": [
            "\033[38;5;238m■\033[0m",  # L0: 0h (Dark Gray)
            "\033[38;5;54m■\033[0m",   # L1: <35% (Dark Plum)
            "\033[38;5;93m■\033[0m",   # L2: <70% (Medium Purple)
            "\033[38;5;129m■\033[0m",  # L3: <100% (Bright Violet)
            "\033[1;38;5;141m■\033[0m" # L4: Goal Met (Neon Purple)
        ]
    }
}

def sanitize_path(path_str):
    if not isinstance(path_str, str):
        return ""
    cleaned = path_str.strip()
    if os.name != 'nt':
        cleaned = cleaned.replace("\\ ", " ").replace("\\-", "-")
        if "\\" in cleaned and not os.path.exists(cleaned):
            cleaned = cleaned.replace("\\", "")
    return cleaned

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
        cfg["target_dir"] = sanitize_path(target_dir)

    cfg.setdefault("focus_sound", None)
    cfg.setdefault("start_sound", None)
    cfg.setdefault("stop_sound", None)
    cfg.setdefault("repeat_focus_sound", False)
    cfg.setdefault("repeat_start_sound", False)

    # Legacy support: migrate repeat_alarm to repeat_stop_sound
    if "repeat_alarm" in cfg:
        if "repeat_stop_sound" not in cfg:
            cfg["repeat_stop_sound"] = bool(cfg.get("repeat_alarm"))
        del cfg["repeat_alarm"]

    cfg.setdefault("repeat_stop_sound", True)

    goal = cfg.get("daily_goal_hours")
    if not isinstance(goal, (int, float)) or not math.isfinite(goal) or goal <= 0 or goal > 24:
        cfg["daily_goal_hours"] = DEFAULT_GOAL_HOURS

    max_b = cfg.get("max_break_minutes")
    if max_b is not None:
        if not isinstance(max_b, (int, float)) or not math.isfinite(max_b) or max_b <= 0:
            cfg["max_break_minutes"] = DEFAULT_MAX_BREAK_MINS

    cutoff = cfg.get("day_cutoff_hour")
    if not isinstance(cutoff, (int, float)) or not math.isfinite(cutoff) or not (0 <= cutoff < 24):
        cfg["day_cutoff_hour"] = DEFAULT_DAY_CUTOFF_HOUR
    else:
        cfg["day_cutoff_hour"] = int(cutoff)

    theme = cfg.get("theme")
    if not isinstance(theme, str) or theme.strip().lower() not in THEME_PALETTES:
        cfg["theme"] = DEFAULT_THEME
    else:
        cfg["theme"] = theme.strip().lower()

    return cfg

def set_theme(theme_str):
    if not theme_str or not isinstance(theme_str, str):
        print("\033[1;31mError: Please specify a valid theme ('green', 'red', 'blue', 'orange', 'purple').\033[0m\n")
        return
    clean_theme = theme_str.strip().lower()
    if clean_theme not in THEME_PALETTES:
        valid_list = ", ".join(f"'{k}'" for k in THEME_PALETTES.keys())
        print(f"\033[1;31mError: Invalid theme '{theme_str}'. Valid options are: {valid_list}.\033[0m\n")
        return

    config = get_config()
    config["theme"] = clean_theme
    save_config(config)
    info = THEME_PALETTES[clean_theme]
    print(f"\033[1;32m✓ Heatmap theme set to: {info['emoji']} {info['name']}\033[0m\n")


def get_logical_date(dt=None):
    """Returns logical work date taking into account user's configured day_cutoff_hour."""
    if dt is None:
        dt = datetime.now()
    config = get_config()
    cutoff = config.get("day_cutoff_hour", 0)
    if isinstance(cutoff, (int, float)) and 0 < cutoff < 24:
        if dt.hour < cutoff:
            return (dt - timedelta(days=1)).date()
    return dt.date()

def set_day_cutoff(hour_str):
    if not hour_str or not isinstance(hour_str, str):
        print("\033[1;31mError: Please enter a valid cutoff hour (0-23, e.g. 3 for 3:00 AM).\033[0m\n")
        return
    try:
        val = float(hour_str)
        if not math.isfinite(val) or val < 0 or val >= 24:
            print("\033[1;31mError: Cutoff hour must be between 0 (midnight) and 23 (e.g. 3 for 3:00 AM).\033[0m\n")
            return
        
        int_val = int(val)
        config = get_config()
        config["day_cutoff_hour"] = int_val
        save_config(config)
        if int_val == 0:
            print("\033[1;32m✓ Day cutoff reset to default (00:00 Midnight).\033[0m\n")
        else:
            print(f"\033[1;32m✓ Day cutoff set to: {int_val}:00 AM (sessions before {int_val}:00 AM count towards previous day)\033[0m\n")
    except ValueError:
        print("\033[1;31mError: Please enter a valid cutoff hour (e.g. 3 for 3:00 AM, 0 for midnight).\033[0m\n")


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

    cleaned = sanitize_path(raw_path)
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
            print("\033[1;31mError: Daily goal must be a positive number greater than 0 hours (e.g. 4.0).\033[0m\n")
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
    config["focus_sound"] = None
    config["start_sound"] = None
    config["stop_sound"] = None
    config["repeat_focus_sound"] = False
    config["repeat_start_sound"] = False
    config["repeat_stop_sound"] = True
    if "repeat_alarm" in config:
        del config["repeat_alarm"]
    save_config(config)
    print("\033[1;32m✓ Audio alerts reset to system default chimes.\033[0m\n")

def set_cue_repeat(cue_key, val_str):
    labels = {
        "focus_sound": "Focus Start",
        "start_sound": "Break Start",
        "stop_sound": "Break End Alarm"
    }
    label = labels.get(cue_key, cue_key)
    if not val_str or not isinstance(val_str, str):
        print(f"\033[1;31mError: Please specify 'on' or 'off' for [{label}] repeat setting.\033[0m\n")
        return
    cleaned = val_str.strip().lower()
    config = get_config()
    if "repeat_alarm" in config:
        del config["repeat_alarm"]
    target_key = f"repeat_{cue_key}"
    if cleaned in ("off", "false", "no", "0", "disable", "disabled", "single"):
        config[target_key] = False
        save_config(config)
        print(f"\033[1;32m✓ Repeat loop for [{label}] disabled (chimes once).\033[0m\n")
    elif cleaned in ("on", "true", "yes", "1", "enable", "enabled", "loop"):
        config[target_key] = True
        save_config(config)
        print(f"\033[1;32m✓ Repeat loop for [{label}] enabled (loops until dismissed).\033[0m\n")
    else:
        print(f"\033[1;31mError: Invalid option for [{label}] repeat. Use 'on' or 'off'.\033[0m\n")


def set_alarm_repeat(val_str):
    set_cue_repeat("stop_sound", val_str)




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

