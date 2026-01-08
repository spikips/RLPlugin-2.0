# have staff of air equipped with all of the runes in inventory
# make sure you have more fire, water, earth runes than law runes
import time, random
from modules.utils.wait_for_tick import wait_for_tick
from modules.widgets.widget import check_widget
from modules.core.plugin_client import stats
from modules.core.window_utils import focus_runelite_window
from modules.widgets.widget import click_widget, check_widget


def get_magic_level_from_stats(stats_dict):
    """Return the player's Magic level from the stats dict or None on failure."""
    try:
        return int(stats_dict['Magic']['level'])
    except Exception as e:
        print('Could not read Magic level from stats:', e)
        return None


def magic_spell_widget_for_level(level):
    """Map a Magic level to the appropriate teleport widget ID.

    Ranges (from repo comments):
    - 25-30 -> '14286871'
    - 31-36 -> '14286874'
    - 37-44 -> '14286877'
    - 45+   -> '14286882'
    Returns the widget id string or None if no mapping.
    """
    if level is None:
        return None
    if 25 <= level <= 30:
        return '14286871'
    if 31 <= level <= 36:
        return '14286874'
    if 37 <= level <= 44:
        return '14286877'
    if level >= 45:
        return '14286882'
    return None


def choose_and_cast_teleport(ensure_tab=True):
    """Choose the teleport widget for the player's Magic level.

    - stats_dict: the dict returned by stats()['data'] (or similar shape)
    - do_click: if True, the function will attempt to open the Magic tab and click the widget
    - ensure_tab: if True and do_click is True, ensure the Magic tab is open before clicking

    Returns: (level, widget_id, clicked_bool)
    """
    level = get_magic_level_from_stats(stats()['data'])
    widget = magic_spell_widget_for_level(level)
    if widget is None:
        print(f'No teleport widget mapped for Magic level: {level}')
        exit()

    print(f'Magic level: {level} -> teleport widget: {widget}')

    # Ensure the magic tab is open (widget id and sprite check taken from this file comments)
    if ensure_tab and not check_widget('35913798', sprite_id=1027):
        click_widget('35913798', rand_x=10, rand_y=10)
        # small wait for tab to open
        for _ in range(50):
            if check_widget('35913798', sprite_id=1027):
                break
            time.sleep(0.05)

    # perform the click (left-click by default)
    click_widget(widget)
    wait_for_tick(4)
    if random.randint(0, 100) == 0:
        wait_ticks = random.randint(1, 50)
        print('Random extra wait for', wait_ticks, 'ticks')
        wait_for_tick(wait_ticks)

focus_runelite_window()
while True:
    choose_and_cast_teleport()