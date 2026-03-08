# 1
import keyboard
from modules.npc_data.click_npc import click_closest_npc
from modules.player_data.wait_till_character_stops_moving import wait_till_character_stopped_moving

from modules.utils.wait_for_tick import wait_for_next_tick
from modules.widgets.widget import click_widget_child


def skip_current_task():
    for i in range(10):
        if not click_closest_npc('vannaka', option='rewards', max_attempts=5):
            wait_for_next_tick()
        else:
            if wait_till_character_stopped_moving(required_idle_ticks=2):
                break
        if i == 9:
            exit("Failed to click npc (vannaka)")


    # 3
    # parent id: 27918349
    for i in range(5):
        if click_widget_child('27918349', sprite_id=None, hidden=None, child_index=6, right_click=False, action=None):
            wait_for_next_tick(1)
            break
        wait_for_next_tick()
        if i == 4:
            exit("Failed to click dialogue option (tasks) via child")

    # 4
    # parent id: 27918363
    for i in range(5):
        if click_widget_child('27918363', sprite_id=None, hidden=None, child_index=0, right_click=False, action=None):
            wait_for_next_tick(1)
            break
        wait_for_next_tick()
        if i == 4:
            exit("Failed to click dialogue option (cancel) via child")

    # parent id: 27918346
    for i in range(5):
        if click_widget_child('27918346', sprite_id=None, hidden=None, child_index=64, right_click=False, action=None):
            keyboard.press_and_release('esc')
            wait_for_next_tick(1)
            break
        wait_for_next_tick()
        if i == 4:
            exit("Failed to click dialogue option (confirm) via child")

# skip_current_task()