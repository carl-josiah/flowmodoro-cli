import os
import json

BREAK_RATIO = 0.2
# Save config in the user's home directory so it's always accessible
USER_HOME = os.path.expanduser("~")
CONFIG_FILE = os.path.join(USER_HOME, ".flowmodoro_config.json")
DEFAULT_TARGET_DIR = os.path.join(USER_HOME, "Documents", "Flowmodoro")

def get_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"target_dir": DEFAULT_TARGET_DIR, "start_sound": None, "stop_sound": None}

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

def set_custom_sound(sound_type, file_path):
    expanded_path = os.path.abspath(os.path.expanduser(file_path.strip()))
    if not os.path.exists(expanded_path):
        print(f"\033[1;31mError: File not found at '{expanded_path}'\033[0m")
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
