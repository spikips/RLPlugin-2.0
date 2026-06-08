import time
import random
import keyboard
from modules.object_data.game_object import click_gameobject
from modules.widgets.widget import click_widget_child, check_widget, check_widget_text
from modules.utils.wait_for_tick import wait_for_tick

# Configurable parameters
INITIAL_SLEEP = 0
MAX_ATTEMPTS = 10
REWARD_CHEST_ID = '26273'
REWARD_CHEST_ACTION = 'Search'
REWARD_CHEST_COORDS = (2609, 3119)
BENEFITS_WIDGET_ID = '13500418'
BENEFITS_CHILD_INDEX = 5
OVL_BUY_X_WIDGET_ID = '13500422'
OVL_BUY_X_CHILD_INDEX = 6
OVL_BUY_X_ACTION = 'buy-x'
ABS_BUY_X_WIDGET_ID = '13500422'
ABS_BUY_X_CHILD_INDEX = 9
ABS_BUY_X_ACTION = 'buy-x'
CHAT_WIDGET_ID = '10616875'
MIN_TYPING_DELAY = 0.039
MAX_TYPING_DELAY = 0.081
ABS_COST = 1000
OVL_COST = 1500

# EXACT TARGETS - WE NEVER BUY MORE THAN THIS
MAX_ABS = 80
MAX_OVL = 28

def get_abs_current():
    absorption = check_widget_text("13500422", child_index=11)
    return int(absorption[1:-1]) if absorption else 0

def get_ovl_current():
    overload = check_widget_text("13500422", child_index=8)
    return int(overload[1:-1]) if overload else 0

def get_reward_points():
    text = check_widget_text('13500418', child_index=6)
    if 'Reward points:' in text:
        points_str = text.split('Reward points: ')[1].strip().replace(',', '')
        return int(points_str)
    return 0

def wait_for_success(condition_func, max_attempts=MAX_ATTEMPTS, attempt_msg="Attempting action"):
    attempt = 0
    while attempt < max_attempts:
        success = condition_func()
        print(f"{attempt_msg}, attempt: {attempt}, success: {success}")
        if success:
            return True
        attempt += 1
        wait_for_tick(1)
    return False

def type_quantity(quantity: str):
    try:
        for char in quantity:
            keyboard.press_and_release(char)
            time.sleep(random.uniform(MIN_TYPING_DELAY, MAX_TYPING_DELAY))
        keyboard.press_and_release('enter')
        print(f"Successfully typed '{quantity}' and pressed Enter.")
    except PermissionError:
        print("Error: Run as administrator/root for global keyboard access.")
        exit('Keyboard permission error')
    except Exception as e:
        print(f"Unexpected error: {e}")
        exit('Unexpected keyboard error')

def open_rewards_chest(retries=3, timeout_ticks=15):
    for attempt in range(1, retries + 1):
        print(f"Opening rewards chest, attempt {attempt}/{retries}")
        click_gameobject(REWARD_CHEST_ID, REWARD_CHEST_ACTION, REWARD_CHEST_COORDS)

        tick_waited = 0
        while tick_waited < timeout_ticks:
            try:
                clicked = click_widget_child(BENEFITS_WIDGET_ID, child_index=BENEFITS_CHILD_INDEX)
            except Exception:
                clicked = False

            if clicked:
                print('Clicked benefits successfully')
                return True

            wait_for_tick(1)
            tick_waited += 1

        print(f"Attempt {attempt} timed out after {timeout_ticks} ticks, retrying...")

    return False

def main(perform_buy=False):
    """
    perform_buy=True  -> opens chest once, checks, buys full remaining set if possible, closes once
    perform_buy=False -> only checks storage and closes (used for initial check)
    """
    time.sleep(INITIAL_SLEEP)

    from modules.core.window_utils import focus_runelite_window
    focus_runelite_window()

    if not open_rewards_chest(retries=3, timeout_ticks=15):
        exit('Benefits failed')

    points = get_reward_points()
    abs_current = get_abs_current()
    ovl_current = get_ovl_current()
    print(f"Reward points: {points}")
    print(f"Current absorption doses: {abs_current}")
    print(f"Current overload doses: {ovl_current}")

    if not perform_buy:
        keyboard.press_and_release('esc')
        print("Storage check complete - rewards UI closed.")
        return {
            'points': points,
            'stored_abs': abs_current,
            'stored_ovl': ovl_current,
            'abs_bought': 0,
            'ovl_bought': 0,
        }

    # === ONLY BUY IF WE CAN AFFORD THE FULL REMAINING SET ===
    needed_abs = max(0, MAX_ABS - abs_current)
    needed_ovl = max(0, MAX_OVL - ovl_current)
    total_cost = needed_abs * ABS_COST + needed_ovl * OVL_COST

    abs_quantity = 0
    overload_quantity = 0

    if points >= total_cost and (needed_abs > 0 or needed_ovl > 0):
        abs_quantity = needed_abs
        overload_quantity = needed_ovl
        print(f"FULL BUY: {abs_quantity} Absorption + {overload_quantity} Overload")
    else:
        print("Not enough points for full remaining set -> skipping purchase")

    # Buy Absorption first
    if abs_quantity > 0:
        if not wait_for_success(lambda: click_widget_child(ABS_BUY_X_WIDGET_ID, child_index=ABS_BUY_X_CHILD_INDEX, action=ABS_BUY_X_ACTION),
                                attempt_msg="Waiting to buy-x tab (absorption)"):
            exit('Absorption buy-x failed')

        if not wait_for_success(lambda: check_widget(CHAT_WIDGET_ID),
                                attempt_msg="Waiting to open chat widget (absorption)"):
            exit('Absorption chat widget failed')

        type_quantity(str(abs_quantity))
        print(f"Typed absorption quantity: {abs_quantity}")

    # Buy Overload after
    if overload_quantity > 0:
        if not wait_for_success(lambda: click_widget_child(OVL_BUY_X_WIDGET_ID, child_index=OVL_BUY_X_CHILD_INDEX, action=OVL_BUY_X_ACTION),
                                attempt_msg="Waiting to buy-x tab (overload)"):
            exit('Overload buy-x failed')

        if not wait_for_success(lambda: check_widget(CHAT_WIDGET_ID),
                                attempt_msg="Waiting to open chat widget (overload)"):
            exit('Overload chat widget failed')

        type_quantity(str(overload_quantity))
        print(f"Typed overload quantity: {overload_quantity}")

    keyboard.press_and_release('esc')

    stored_abs = abs_current + abs_quantity
    stored_ovl = ovl_current + overload_quantity

    return {
        'points': points,
        'stored_abs': stored_abs,
        'stored_ovl': stored_ovl,
        'abs_bought': abs_quantity,
        'ovl_bought': overload_quantity,
    }

if __name__ == "__main__":
    main(perform_buy=True)