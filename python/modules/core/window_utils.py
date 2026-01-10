import time
import pygetwindow as gw
import win32gui
import pyautogui
from ctypes import windll, Structure, c_long, byref
from typing import Tuple, Optional

class POINT(Structure):
    _fields_ = [("x", c_long), ("y", c_long)]

def find_canvas_hwnd(parent_hwnd):
    canvas_hwnd = [None]

    def enum_callback(hwnd, lparam):
        class_name = win32gui.GetClassName(hwnd)
        if class_name == "SunAwtCanvas":
            canvas_hwnd[0] = hwnd
            return False
        return True

    win32gui.EnumChildWindows(parent_hwnd, enum_callback, 0)
    return canvas_hwnd[0]

# Lazy cache for canvas coordinates
_cached_runelite_coords: Optional[Tuple[int, int, int, int]] = None

def get_runelite_window_coords() -> Optional[Tuple[int, int, int, int]]:
    """Lazy compute canvas coordinates - only runs when first called."""
    global _cached_runelite_coords
    if _cached_runelite_coords is not None:
        return _cached_runelite_coords

    print("Detecting RuneLite canvas...")

    # Get all RuneLite windows
    runelite_windows = [w for w in gw.getWindowsWithTitle('RuneLite') if w.title == 'RuneLite']
    if not runelite_windows:
        print("RuneLite window not found.")
        return None

    # Use the active or first visible one
    active_window = gw.getActiveWindow()
    if active_window and active_window.title == 'RuneLite':
        runelite_window = active_window
    else:
        runelite_window = runelite_windows[0]

    # Ensure window is visible and not minimized
    if runelite_window.isMinimized:
        print("RuneLite window is minimized - restoring...")
        runelite_window.restore()
        time.sleep(0.5)

    hwnd = runelite_window._hWnd
    canvas_hwnd = find_canvas_hwnd(hwnd)
    if not canvas_hwnd:
        print("RuneLite canvas not found.")
        return None

    # Get canvas rect relative to parent
    rect = win32gui.GetWindowRect(canvas_hwnd)
    parent_rect = win32gui.GetWindowRect(hwnd)
    canvas_x = rect[0] - parent_rect[0]
    canvas_y = rect[1] - parent_rect[1]
    canvas_width = rect[2] - rect[0]
    canvas_height = rect[3] - rect[1]

    # Absolute screen position of canvas
    screen_x = rect[0]
    screen_y = rect[1]

    _cached_runelite_coords = (screen_x, screen_y, canvas_width, canvas_height)
    print(f"RuneLite canvas detected: x={screen_x}, y={screen_y}, w={canvas_width}, h={canvas_height}")
    return _cached_runelite_coords

def runelite_window(rel_x: int, rel_y: int) -> Tuple[int, int]:
    coords = get_runelite_window_coords()
    if coords is None:
        print("Unable to get RuneLite coordinates - returning (0,0)")
        return (0, 0)
    screen_x, screen_y, _, _ = coords
    return (screen_x + rel_x, screen_y + rel_y)

# Focus state
_focused_runelite_once = False

def focus_runelite_window() -> bool:
    global _focused_runelite_once
    if _focused_runelite_once:
        return True

    print("Attempting to focus RuneLite window...")

    runelite_windows = [w for w in gw.getWindowsWithTitle('RuneLite') if w.title == 'RuneLite']
    if not runelite_windows:
        print("RuneLite window not found.")
        return False

    runelite_window = runelite_windows[0]

    # Restore if minimized
    if runelite_window.isMinimized:
        print("RuneLite window minimized - restoring...")
        runelite_window.restore()
        time.sleep(0.5)

    hwnd = runelite_window._hWnd

    # Check if already foreground
    if win32gui.GetForegroundWindow() == hwnd:
        print("RuneLite already in foreground.")
        _focused_runelite_once = True
        return True

    pyautogui.press('alt')
    try:
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.2)
        print("Focused RuneLite window successfully.")
        _focused_runelite_once = True
        return True
    except Exception as e:
        print(f"Failed to focus RuneLite: {e}")
        return False

def reset_window_cache():
    global _cached_runelite_coords, _focused_runelite_once
    _cached_runelite_coords = None
    _focused_runelite_once = False
    print("Window cache reset.")
    return True