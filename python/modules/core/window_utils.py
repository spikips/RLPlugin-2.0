import time
import pygetwindow as gw
import win32gui
import pyautogui
from ctypes import windll, Structure, c_long, byref

class POINT(Structure):
    _fields_ = [("x", c_long), ("y", c_long)]

def find_canvas_hwnd(parent_hwnd):
    """
    Callback function to find the SunAwtCanvas child window.
    """
    canvas_hwnd = [None]  # Use list to mutate inside callback

    def enum_callback(hwnd, lparam):
        class_name = win32gui.GetClassName(hwnd)
        if class_name == "SunAwtCanvas":
            canvas_hwnd[0] = hwnd
            return False  # Stop enumeration
        return True

    win32gui.EnumChildWindows(parent_hwnd, enum_callback, 0)
    return canvas_hwnd[0]

def get_runelite_window_coords():
    """
    Retrieve the accurate screen coordinates and size of the RuneLite game canvas.
    
    Returns:
        tuple: (screen_x, screen_y, width, height) of the canvas area, or None if not found.
    """
    # Use cached coordinates when available to avoid repeated expensive
    # window enumeration and ClientToScreen calls. This function will compute
    # the coords once per process run and return the cached value afterwards.
    global _cached_runelite_coords
    try:
        if _cached_runelite_coords is not None:
            return _cached_runelite_coords
    except NameError:
        _cached_runelite_coords = None

    runelite_windows = [w for w in gw.getWindowsWithTitle('RuneLite') if w.title == 'RuneLite']
    if not runelite_windows:
        print("RuneLite window not found.")
        return None

    runelite_window = runelite_windows[0]
    parent_hwnd = runelite_window._hWnd  # Parent window handle

    # Find the child canvas hwnd
    canvas_hwnd = find_canvas_hwnd(parent_hwnd)
    if not canvas_hwnd:
        print("RuneLite game canvas not found.")
        return None

    # Get canvas client area dimensions
    rect = win32gui.GetClientRect(canvas_hwnd)
    width = rect[2] - rect[0]
    height = rect[3] - rect[1]

    # Convert canvas (0,0) to screen coordinates
    pt = POINT(0, 0)
    windll.user32.ClientToScreen(canvas_hwnd, byref(pt))
    screen_x, screen_y = pt.x, pt.y

    _cached_runelite_coords = (screen_x, screen_y, width, height)
    print(f"RuneLite game canvas screen coordinates: (x: {screen_x}, y: {screen_y}, width: {width}, height: {height})")
    return _cached_runelite_coords

def runelite_window(x: int, y: int) -> tuple[int, int]:
    """
    Convert canvas coordinates to screen coordinates relative to the RuneLite game canvas.

    Args:
        x (int): X-coordinate in canvas space.
        y (int): Y-coordinate in canvas space.

    Returns:
        tuple[int, int]: Screen coordinates (x, y).
    """
    coords = get_runelite_window_coords()
    if coords:
        screen_x, screen_y, _, _ = coords
        return x + screen_x, y + screen_y
    return x, y

def focus_runelite_window():
    """
    Bring the RuneLite window to the foreground to ensure keyboard inputs register, only if not already focused.
    """
    # Only perform focus the first time this is called. Subsequent calls
    # will be fast no-ops unless `reset_window_cache()` is called.
    global _focused_runelite_once
    try:
        if _focused_runelite_once:
            return True
    except NameError:
        _focused_runelite_once = False

    runelite_windows = [w for w in gw.getWindowsWithTitle('RuneLite') if w.title == 'RuneLite']
    if not runelite_windows:
        print("RuneLite window not found.")
        return False
    runelite_window = runelite_windows[0]
    hwnd = runelite_window._hWnd
    # Workaround for SetForegroundWindow error: Press Alt first
    pyautogui.press('alt')
    win32gui.SetForegroundWindow(hwnd)
    time.sleep(0.05)  # Small delay for focus to take effect
    _focused_runelite_once = True
    print("Debug: Focused RuneLite window.")
    return True

def reset_window_cache():
    """Reset cached RuneLite window coordinates and focus state.

    Call this if the window has been moved/resized or if you want to force
    re-acquisition of coordinates/focus.
    """
    global _cached_runelite_coords, _focused_runelite_once
    _cached_runelite_coords = None
    _focused_runelite_once = False
    return True