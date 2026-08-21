import os
import json

BREAK_RATIO = 0.2
DEFAULT_GOAL_HOURS = 6.0
DEFAULT_MAX_BREAK_MINS = None
USER_HOME = os.path.expanduser("~")
CONFIG_FILE = os.path.join(USER_HOME, ".flowmodoro_config.json")
DEFAULT_TARGET_DIR = os.path.join(USER_HOME, "Documents", "Flowmodoro")

def get_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                cfg.setdefault("target_dir", DEFAULT_TARGET_DIR)
                cfg.setdefault("start_sound", None)
                cfg.setdefault("stop_sound", None)
                cfg.setdefault("daily_goal_hours", DEFAULT_GOAL_HOURS)
                cfg.setdefault("max_break_minutes", DEFAULT_MAX_BREAK_MINS)
                cfg.setdefault("ntfy_topic", None)
                return cfg
        except Exception:
            pass
    return {
        "target_dir": DEFAULT_TARGET_DIR,
        "start_sound": None,
        "stop_sound": None,
        "daily_goal_hours": DEFAULT_GOAL_HOURS,
        "max_break_minutes": DEFAULT_MAX_BREAK_MINS,
        "ntfy_topic": None
    }

def save_config(config_data):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=2)

def set_persistent_directory(raw_path):
    expanded_path = os.path.abspath(os.path.expanduser(raw_path.strip()))
    os.makedirs(expanded_path, exist_ok=True)
    config = get_config()
    config["target_dir"] = expanded_path
    save_config(config)
    print(f"\033[1;32m✓ Persistent log path set to:\033[0m\n  📂 {expanded_path}\n")

def set_daily_goal(hours_str):
    try:
        hours = float(hours_str)
        if hours <= 0:
            print("\033[1;31mError: Daily goal must be greater than 0 hours.\033[0m\n")
            return
        config = get_config()
        config["daily_goal_hours"] = round(hours, 2)
        save_config(config)
        print(f"\033[1;32m✓ Daily deep work goal set to: {hours:g} hours/day\033[0m\n")
    except ValueError:
        print("\033[1;31mError: Please enter a valid number of hours (e.g. 4, 6.5, 8).\033[0m\n")

def set_max_break(minutes_str):
    try:
        mins = float(minutes_str)
        config = get_config()
        if mins <= 0:
            config["max_break_minutes"] = None
            save_config(config)
            print("\033[1;32m✓ Maximum break cap disabled (unlimited earned rest).\033[0m\n")
        else:
            config["max_break_minutes"] = round(mins, 1)
            save_config(config)
            print(f"\033[1;32m✓ Maximum break duration capped at: {mins:g} minutes\033[0m\n")
    except ValueError:
        print("\033[1;31mError: Please enter a valid number of minutes (e.g. 15, 20, 30).\033[0m\n")

def set_notify_topic(topic_str):
    topic = topic_str.strip()
    config = get_config()
    if not topic or topic.lower() in ["off", "disable", "none"]:
        config["ntfy_topic"] = None
        save_config(config)
        print("\033[1;32m✓ Phone notifications disabled.\033[0m\n")
        return

    config["ntfy_topic"] = topic
    save_config(config)
    print(f"\033[1;32m✓ Phone notification channel set to:\033[0m")
    print(f"  📱 Topic: \033[1;36m{topic}\033[0m")
    print(f"  Install 'ntfy' on iOS/Android & subscribe to '{topic}' to receive instant push alerts.\n")

def set_custom_sound(sound_type, file_path):
    expanded_path = os.path.abspath(os.path.expanduser(file_path.strip()))
    if not os.path.exists(expanded_path):
        print(f"\033[1;31mError: File not found at '{expanded_path}'\033[0m\n")
        return
    config = get_config()
    config[sound_type] = expanded_path
    save_config(config)
    print(f"\033[1;32m✓ Custom audio saved for [{sound_type}]:\033[0m\n  🎵 {expanded_path}\n")

def reset_sound_defaults():
    config = get_config()
    config["start_sound"] = None
    config["stop_sound"] = None
    save_config(config)
    print("\033[1;32m✓ Audio alerts reset to system default chimes.\033[0m\n")

def get_active_paths():
    config = get_config()
    target_dir = config.get("target_dir", DEFAULT_TARGET_DIR)
    os.makedirs(target_dir, exist_ok=True)
    return (
        target_dir,
        os.path.join(target_dir, "flowmodoro_data.jsonl"),
        os.path.join(target_dir, "flowmodoro_log.md")
    )
