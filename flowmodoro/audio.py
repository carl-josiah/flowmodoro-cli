import os
import sys
import subprocess
import platform
import threading
from .config import get_config, set_custom_sound

# --- Desktop Banner Notifications ---
def send_desktop_notification(title, message):
    """Zero-dependency desktop notification for macOS, Linux, and Windows."""
    system = platform.system()
    safe_title = str(title).replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ")
    safe_msg = str(message).replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ")

    try:
        if system == "Darwin":  # macOS
            script = f'display notification "{safe_msg}" with title "{safe_title}" sound name "Glass"'
            subprocess.Popen(["osascript", "-e", script], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif system == "Linux":
            if os.system("which notify-send > /dev/null 2>&1") == 0:
                subprocess.Popen(["notify-send", safe_title, safe_msg], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif system == "Windows":
            ps_title = safe_title.replace("'", "''")
            ps_msg = safe_msg.replace("'", "''")
            ps_cmd = (
                '[void] [System.Reflection.Assembly]::LoadWithPartialName("System.Windows.Forms"); '
                '$notify = New-Object System.Windows.Forms.NotifyIcon; '
                '$notify.Icon = [System.Drawing.SystemIcons]::Information; '
                '$notify.Visible = $true; '
                f"$notify.ShowBalloonTip(5000, '{ps_title}', '{ps_msg}', [System.Windows.Forms.ToolTipIcon]::Info);"
            )
            subprocess.Popen(["powershell", "-c", ps_cmd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

# --- System Sound Discovery & Browser ---
def get_system_sound_dir():
    system = platform.system()
    if system == "Darwin":
        return "/System/Library/Sounds", [".aiff", ".caf"]
    elif system == "Windows":
        return r"C:\Windows\Media", [".wav"]
    elif system == "Linux":
        return "/usr/share/sounds/freedesktop/stereo", [".oga", ".ogg", ".wav"]
    return None, []

def list_system_sounds():
    sound_dir, valid_exts = get_system_sound_dir()
    if not sound_dir or not os.path.exists(sound_dir):
        return []
    
    sounds = []
    try:
        for f in sorted(os.listdir(sound_dir)):
            ext = os.path.splitext(f)[1].lower()
            if ext in valid_exts:
                sounds.append({
                    "name": os.path.splitext(f)[0].capitalize(),
                    "path": os.path.join(sound_dir, f)
                })
    except Exception:
        pass
    return sounds

def interactive_system_sound_picker():
    sounds = list_system_sounds()
    if not sounds:
        print("\n\033[1;31mNo native system sounds found on this OS.\033[0m\n")
        return

    os.system('cls' if os.name == 'nt' else 'clear')
    print("=" * 60)
    print("           🎵 SELECT NATIVE SYSTEM SOUNDS")
    print("=" * 60)
    print("\nAvailable built-in sounds on your machine:\n")
    for i, snd in enumerate(sounds):
        print(f"  [{i+1:<2}] {snd['name']}")
    print("=" * 60)

    print("\nWhich alert do you want to configure?")
    print("  [1] Focus Complete (Break Start tone)")
    print("  [2] Earned Break Ended (Alarm tone)")
    try:
        target_choice = input("Select [1 or 2, or 'q' to quit]: ").strip().lower()
    except (KeyboardInterrupt, EOFError):
        print("\nCanceled.\n")
        return

    if target_choice not in ['1', '2']:
        print("Canceled.\n")
        return
    
    target_key = "start_sound" if target_choice == '1' else "stop_sound"
    target_label = "Break Start" if target_choice == '1' else "Break End Alarm"

    while True:
        try:
            choice = input(f"\nEnter sound # to preview & select for [{target_label}] (or 'q' to exit): ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            print("\nCanceled.\n")
            return

        if choice == 'q' or not choice:
            print("Canceled.\n")
            return
        
        if choice.isdigit() and 1 <= int(choice) <= len(sounds):
            selected = sounds[int(choice) - 1]
            play_sound_file(selected["path"])
            print(f"🔊 Playing preview: \033[1;36m{selected['name']}\033[0m")
            
            try:
                confirm = input(f"Set '{selected['name']}' as your {target_label} sound? [Y/n]: ").strip().lower()
            except (KeyboardInterrupt, EOFError):
                print("\nCanceled.\n")
                return

            if confirm != 'n':
                set_custom_sound(target_key, selected["path"])
                break
        else:
            print("\033[1;31mInvalid number. Try again.\033[0m")

def play_sound_file(file_path):
    if not file_path or not isinstance(file_path, str) or not os.path.isfile(file_path):
        return

    system = platform.system()
    try:
        if system == "Darwin":
            subprocess.Popen(["afplay", file_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif system == "Windows":
            safe_path = file_path.replace("'", "''")
            ps_cmd = (
                f"Add-Type -AssemblyName presentationCore; "
                f"$player = New-Object System.Windows.Media.MediaPlayer; "
                f"$player.Open([System.Uri]'{safe_path}'); "
                f"$player.Play(); Start-Sleep -Milliseconds 1500"
            )
            subprocess.Popen(["powershell", "-c", ps_cmd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif system == "Linux":
            for tool in ["mpv", "ffplay", "paplay", "aplay", "cvlc"]:
                if os.system(f"which {tool} > /dev/null 2>&1") == 0:
                    cmd = ["ffplay", "-nodisp", "-autoexit", file_path] if tool == "ffplay" else [tool, file_path]
                    subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    return
    except Exception:
        pass

def play_default_beep():
    system = platform.system()
    sys.stdout.write('\a')
    sys.stdout.flush()
    try:
        if system == "Windows":
            import ctypes
            windll = getattr(ctypes, 'windll', None)
            if windll:
                windll.kernel32.Beep(1000, 350)
            else:
                subprocess.Popen(["powershell", "-c", "[console]::beep(1000, 350)"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif system == "Darwin":
            subprocess.Popen(["afplay", "/System/Library/Sounds/Glass.aiff"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif system == "Linux":
            for cmd in [["paplay", "/usr/share/sounds/freedesktop/stereo/complete.oga"], ["aplay", "/usr/share/sounds/alsa/Front_Center.wav"]]:
                if os.system(f"which {cmd[0]} > /dev/null 2>&1") == 0:
                    subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    break
    except Exception:
        pass

def trigger_alert(sound_type="stop_sound"):
    config = get_config()
    sound_path = config.get(sound_type)
    if sound_path and os.path.exists(sound_path) and os.path.isfile(sound_path):
        play_sound_file(sound_path)
    else:
        play_default_beep()

def ring_alarm_until_dismissed():
    stop_event = threading.Event()
    
    # Trigger desktop banner
    send_desktop_notification("⚡ Flowmodoro", "Break is complete! Time to resume your deep work session.")

    def _alarm_loop():
        while not stop_event.is_set():
            trigger_alert("stop_sound")
            stop_event.wait(1.8)

    alarm_thread = threading.Thread(target=_alarm_loop, daemon=True)
    alarm_thread.start()
    print("\n\n\033[1;33m>>> Break complete! Press [Enter] to dismiss alarm and start next session... <<<\033[0m")
    try:
        input()
    except (KeyboardInterrupt, EOFError):
        pass
    finally:
        stop_event.set()
        alarm_thread.join()

