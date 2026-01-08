import ctypes
import math
import random
import time
import sys

# Import necessary Windows API functions
user32 = ctypes.WinDLL('user32', use_last_error=True)

def move_mouse(x, y):
    if x == 0 and y == 0:
        print("Failsafe triggered: Mouse at (0, 0), exiting program")
        sys.exit(1)
    user32.SetCursorPos(int(x), int(y))

def get_cursor_pos():
    class POINT(ctypes.Structure):
        _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]
    pt = POINT()
    user32.GetCursorPos(ctypes.byref(pt))
    return (pt.x, pt.y)

def hypotenuse(dx, dy):
    return math.hypot(dx, dy)

# Mouse event constants
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_MIDDLEDOWN = 0x0020
MOUSEEVENTF_MIDDLEUP = 0x0040
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_WHEEL = 0x0800

def mouse_event(dwFlags, dwData=0):
    user32.mouse_event(dwFlags, 0, 0, dwData, 0)

def click_down(button):
    if button == 'left':
        mouse_event(MOUSEEVENTF_LEFTDOWN)
    elif button == 'middle':
        mouse_event(MOUSEEVENTF_MIDDLEDOWN)
    elif button == 'right':
        mouse_event(MOUSEEVENTF_RIGHTDOWN)

def click_up(button):
    if button == 'left':
        mouse_event(MOUSEEVENTF_LEFTUP)
    elif button == 'middle':
        mouse_event(MOUSEEVENTF_MIDDLEUP)
    elif button == 'right':
        mouse_event(MOUSEEVENTF_RIGHTUP)

def left_click():
    click_down('left')
    time.sleep(0.05)
    click_up('left')

def middle_click():
    click_down('middle')
    time.sleep(0.05)
    click_up('middle')

def right_click():
    click_down('right')
    time.sleep(0.05)
    click_up('right')

async def wind_mouse(dest_x, dest_y, gravity=15, wind=4, max_step=35, target_area=20, speed=2, step_delay=0.003):
    sqrt3 = math.sqrt(3)
    sqrt5 = math.sqrt(5)
    rand = random.Random()

    current_x, current_y = get_cursor_pos()

    velocity_x = 0
    velocity_y = 0
    wind_x = 0
    wind_y = 0

    iteration = 0

    while True:
        delta_x = dest_x - current_x
        delta_y = dest_y - current_y
        distance = hypotenuse(delta_x, delta_y)

        if distance < 1:
            break

        wind_mag = min(wind, distance)

        if distance >= target_area:
            wind_x = wind_x / sqrt3 + (2 * rand.random() - 1) * wind_mag / sqrt5
            wind_y = wind_y / sqrt3 + (2 * rand.random() - 1) * wind_mag / sqrt5
        else:
            wind_x /= sqrt5
            wind_y /= sqrt5
            max_step = max(max_step / sqrt5, 3)

        velocity_x += wind_x + gravity * delta_x / distance
        velocity_y += wind_y + gravity * delta_y / distance

        velocity_mag = hypotenuse(velocity_x, velocity_y)
        if velocity_mag > max_step:
            random_displacement = max_step / 2.0 + rand.random() * max_step / 2.0
            velocity_x = (velocity_x / velocity_mag) * random_displacement
            velocity_y = (velocity_y / velocity_mag) * random_displacement

        prev_x = current_x
        prev_y = current_y
        current_x += int(round(velocity_x))
        current_y += int(round(velocity_y))

        if prev_x != current_x or prev_y != current_y:
            move_mouse(current_x, current_y)

        if iteration % speed == 0:
            time.sleep(step_delay)

        iteration += 1

def move(x=None, y=None, fast=False, button=None, drag=False, speed=2, sleep=False):
    # Check current cursor position for failsafe
    current_x, current_y = get_cursor_pos()
    if current_x == 0 and current_y == 0:
        print("Failsafe triggered: Mouse at (0, 0), exiting program")
        sys.exit(1)

    if drag and button:
        # Perform drag: press and hold the mouse button, move, then release
        click_down(button)
        # time.sleep(0.03)
        # Move the mouse while holding the button
        if fast:
            move_mouse(x, y)
        else:
            import asyncio
            asyncio.run(wind_mouse(x, y, speed=speed))
        time.sleep(0.03)

        # Release the mouse button
        click_up(button)
    else:
        # Move the mouse if coordinates are provided
        if x is not None and y is not None:
            if fast:
                move_mouse(x, y)
                if sleep:
                    time.sleep(0.05)
            else:
                import asyncio
                asyncio.run(wind_mouse(x, y))
        # Handle clicks after moving (or if no move)
        if button == 'left':
            left_click()
        elif button == 'middle':
            middle_click()
        elif button == 'right':
            right_click()

def scroll(direction, sleep=0.1):
    """
    Scroll the mouse wheel.
    :param direction: Positive integer to scroll up, negative to scroll down.
    """
    wheel_delta = 120 if direction > 0 else -120
    mouse_event(MOUSEEVENTF_WHEEL, wheel_delta)
    time.sleep(sleep)  # Small delay for stability