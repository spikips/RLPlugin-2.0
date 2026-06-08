import random
import time
import keyboard
from modules.widgets.widget_data import get_widget_by_id
from modules.core.mouse_control import move as mouse_click
from modules.core.window_utils import runelite_window

def check_prayer_spellbook():
    """
    Check if the prayer spellbook is open using fast single-widget lookup.
    Opens it with F2 if needed.
    """
    SPELLBOOK_WIDGET_ID = 35913797   # This is the prayer tab/button

    # Fast check - only 1 widget
    widget = get_widget_by_id(SPELLBOOK_WIDGET_ID)
    if widget and widget.get("spriteId") == 1030:
        print("Prayer spellbook is already open.")
        return True

    # Not open → press F2
    print("Prayer spellbook is closed, attempting to open...")
    print('opening prayer book')
    keyboard.press_and_release('f2')
    time.sleep(0.2)  # Small delay for interface to update

    # Fast verification after pressing F2
    widget = get_widget_by_id(SPELLBOOK_WIDGET_ID)
    if widget and widget.get("spriteId") == 1030:
        print("Successfully opened prayer spellbook.")
        return True
    else:
        print("Failed to open prayer spellbook (or widget not found).")
        return False


# For testing
# check_prayer_spellbook()