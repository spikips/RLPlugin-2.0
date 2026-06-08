import time
import random
import keyboard
from modules.object_data.game_object import click_gameobject
from modules.widgets.widget import check_widget, check_widget_text
from modules.utils.wait_for_tick import wait_for_tick
from modules.core.plugin_client import player
from potions import get_total_doses
from modules.utils.drop_item import open_inventory_tab

# Configurable parameters
INITIAL_SLEEP = 0  # seconds
MAX_ATTEMPTS = 5
MAX_TICKS = 10
MIN_TYPING_DELAY = 0.039
MAX_TYPING_DELAY = 0.081
OVERLOAD_BARREL_ID = "26279"
OVERLOAD_ACTION = "Take overload potion"
OVERLOAD_TILE = (2600, 3116)
OVERLOAD_DESIRED_DOSES = 28
ABSORPTION_BARREL_ID = "26280"
ABSORPTION_ACTION = "Take absorption potion"
ABSORPTION_TILE = (2600, 3117)
ABSORPTION_DESIRED_DOSES = 80
CHAT_WIDGET_ID = "10616875"


def get_stored_counts():
    try:
        abs_text = check_widget_text("13500422", child_index=11)
        ovl_text = check_widget_text("13500422", child_index=8)
        if abs_text is None or ovl_text is None:
            return (None, None)
        stored_abs = int(abs_text[1:-1]) if isinstance(abs_text, str) and abs_text.startswith('(') else int(abs_text)
        stored_ovl = int(ovl_text[1:-1]) if isinstance(ovl_text, str) and ovl_text.startswith('(') else int(ovl_text)
        return (stored_abs, stored_ovl)
    except Exception:
        return (None, None)

def wait_for_success(condition_func, max_attempts=MAX_ATTEMPTS, max_ticks=MAX_TICKS, attempt_msg="Attempting action"):
    for attempt in range(max_attempts):
        print(f"{attempt_msg}, attempt {attempt + 1}/{max_attempts}")
        tick_count = 0
        while tick_count < max_ticks:
            success = condition_func()
            if success:
                print(f"{attempt_msg} succeeded on attempt {attempt + 1}, tick {tick_count + 1}")
                return True
            wait_for_tick(1)
            tick_count += 1
        print(f"{attempt_msg} failed after {max_ticks} ticks on attempt {attempt + 1}")
    print(f"{attempt_msg} failed after {max_attempts} attempts")
    return False

def check_player_proximity(tile, max_distance=20):
    player_data = player(location=True)
    if not player_data or 'data' not in player_data or 'location' not in player_data['data']:
        print("Failed to retrieve player location.")
        return False
    player_x = player_data['data']['location']['x']
    player_y = player_data['data']['location']['y']
    target_x, target_y = tile
    distance = abs(player_x - target_x) + abs(player_y - target_y)
    if distance <= max_distance:
        print(f"Player is within {distance} tiles of target {tile}")
        return True
    print(f"Player is {distance} tiles away from target {tile}, too far (max {max_distance})")
    return False

def type_quantity(quantity: int):
    try:
        quantity_str = str(quantity)
        for char in quantity_str:
            keyboard.press_and_release(char)
            time.sleep(random.uniform(MIN_TYPING_DELAY, MAX_TYPING_DELAY))
        keyboard.press_and_release('enter')
        print(f"Successfully typed '{quantity_str}' and pressed Enter.")
        time.sleep(random.uniform(MIN_TYPING_DELAY, MAX_TYPING_DELAY))
    except PermissionError:
        print("Error: Run as administrator/root for global keyboard access.")
        exit('Keyboard permission error')
    except Exception as e:
        print(f"Unexpected error: {e}")
        exit('Unexpected keyboard error')

def withdraw_potion(barrel_id, action, tile, quantity, potion_name, desired_doses):
    if quantity <= 0:
        print(f"No need to withdraw {potion_name}: Already at or above desired doses.")
        return True

    initial_total = get_total_doses(potion_name.lower())

    if not check_player_proximity(tile, max_distance=20):
        print(f"Cannot withdraw {potion_name}: Player too far from barrel.")
        return False

    for attempt in range(MAX_ATTEMPTS):
        print(f"Attempting to withdraw {potion_name} ({quantity} doses), attempt {attempt + 1}/{MAX_ATTEMPTS}")
        if not click_gameobject(barrel_id, action, tile):
            print(f"Failed to click {potion_name} barrel on attempt {attempt + 1}")
            open_inventory_tab()
            wait_for_tick(1)
            continue

        print(f"Clicked {potion_name} barrel successfully")
        
        if wait_for_success(lambda: check_widget(CHAT_WIDGET_ID),
                           max_attempts=1,
                           max_ticks=MAX_TICKS,
                           attempt_msg=f"Waiting for chat widget ({potion_name})"):
            try:
                chat_text = check_widget_text(CHAT_WIDGET_ID) or ""
            except Exception:
                chat_text = ""

            empty_indicators = ['no doses', 'no potion', 'no potions', 'nothing left', 'out of', 'not enough', 'there are no']
            if any(ind in chat_text.lower() for ind in empty_indicators):
                print(f"Barrel appears empty for {potion_name}: '{chat_text}'. Skipping.")
                return True

            print(f"Withdrawing {potion_name}")
            type_quantity(quantity)
            wait_for_tick(2)
            
            new_total = get_total_doses(potion_name.lower())
            if new_total >= desired_doses:
                print(f"Withdrew {potion_name} successfully, total doses: {new_total}")
                return True
            if new_total > initial_total:
                gained = new_total - initial_total
                print(f"Partially withdrew {potion_name}: gained {gained} doses (total {new_total})")
                return True

        print(f"Chat widget not found for {potion_name} after attempt {attempt + 1}")
        wait_for_tick(1)

    final_total = get_total_doses(potion_name.lower())
    if final_total > initial_total:
        gained = final_total - initial_total
        print(f"Partially withdrew {potion_name}: gained {gained} doses (total {final_total}).")
        return True

    print(f"Failed to withdraw {potion_name} after {MAX_ATTEMPTS} attempts.")
    return False

def main(stored_abs=None, stored_ovl=None):
    time.sleep(INITIAL_SLEEP)

    if stored_abs is None or stored_ovl is None:
        stored_abs_read, stored_ovl_read = get_stored_counts()
        if stored_abs is None:
            stored_abs = stored_abs_read
        if stored_ovl is None:
            stored_ovl = stored_ovl_read

    if stored_abs is not None and stored_ovl is not None:
        print(f"Stored counts from rewards UI: Absorption={stored_abs}, Overload={stored_ovl}")

    # Overload withdrawal
    current_overload = get_total_doses("overload")
    overload_needed = max(0, OVERLOAD_DESIRED_DOSES - current_overload)
    if stored_ovl == 0:
        overload_needed = 0

    if overload_needed > 0:
        print(f"Withdrawing overload: need {overload_needed} doses")
        withdraw_potion(OVERLOAD_BARREL_ID, OVERLOAD_ACTION, OVERLOAD_TILE, overload_needed, "Overload", OVERLOAD_DESIRED_DOSES)

    wait_for_tick(1)

    # Absorption withdrawal (now fixed)
    current_absorption = get_total_doses("absorption")
    absorption_needed = max(0, ABSORPTION_DESIRED_DOSES - current_absorption)
    if stored_abs == 0:
        absorption_needed = 0

    if absorption_needed > 0:
        print(f"Withdrawing absorption: need {absorption_needed} doses")
        withdraw_potion(ABSORPTION_BARREL_ID, ABSORPTION_ACTION, ABSORPTION_TILE, absorption_needed, "Absorption", ABSORPTION_DESIRED_DOSES)
    else:
        print("No absorption withdrawal necessary.")

    print("Barrel withdrawal complete.")
    return True

if __name__ == "__main__":
    main()