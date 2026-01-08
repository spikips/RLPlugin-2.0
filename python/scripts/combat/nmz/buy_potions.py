import time
import random  # For random delays
import keyboard
from modules.object_data.game_object import click_gameobject
from modules.widgets.widget import click_widget_child, check_widget, check_widget_text
from modules.utils.wait_for_tick import wait_for_tick

# Configurable parameters
INITIAL_SLEEP = 0  # seconds
MAX_ATTEMPTS = 10
REWARD_CHEST_ID = '26273'
REWARD_CHEST_ACTION = 'Search'
REWARD_CHEST_COORDS = (2609, 3119)
BENEFITS_WIDGET_ID = '13500418'
BENEFITS_CHILD_INDEX = 5
OVL_BUY_X_WIDGET_ID = '13500422'  # overload
OVL_BUY_X_CHILD_INDEX = 6  # overload
OVL_BUY_X_ACTION = 'buy-x'  # overload
ABS_BUY_X_WIDGET_ID = '13500422'  # absorption
ABS_BUY_X_CHILD_INDEX = 9  # absorption
ABS_BUY_X_ACTION = 'buy-x'  # absorption
CHAT_WIDGET_ID = '10616875'
MIN_TYPING_DELAY = 0.039  # seconds (lower bound for random delay)
MAX_TYPING_DELAY = 0.081  # seconds (upper bound for random delay)
ABS_COST = 1000  # points per absorption dose
OVL_COST = 1500  # points per overload dose
MIN_POINTS_THRESHOLD = 4000  # min points to proceed
FULL_STOCK_POINTS = 136000  # threshold for full stock buy (28 abs + 72 ovl max cost)
MAX_ABS = 28  # target absorption doses
MAX_OVL = 72  # target overload doses

def get_abs_current():
    """
    Retrieves current absorption doses from widget text.
    - Helps in understanding: Parses UI for stored doses.
    - Bigger picture: Supports conditional purchasing based on existing stock.
    """
    absorption = check_widget_text("13500422", child_index=11)
    return int(absorption[1:-1])  # Remove parentheses and convert to int

def get_ovl_current():
    """
    Retrieves current overload doses from widget text.
    - Helps in understanding: Parses UI for stored doses.
    - Bigger picture: Supports conditional purchasing based on existing stock.
    """
    overload = check_widget_text("13500422", child_index=8)
    return int(overload[1:-1])  # Remove parentheses and convert to int

def get_reward_points():
    """
    Parses reward points from widget text.
    - Helps understand: Extracts numeric value reliably, handling commas.
    - Bigger picture: Enables point-based decisions without manual checks.
    """
    text = check_widget_text('13500418', child_index=6)
    if 'Reward points:' in text:
        points_str = text.split('Reward points: ')[1].strip().replace(',', '')
        return int(points_str)
    return 0

def wait_for_success(condition_func, max_attempts=MAX_ATTEMPTS, attempt_msg="Attempting action"):
    """
    Generic waiter: Retries a condition function until success or max attempts reached.
    - Helps understand: Abstracts retry logic for reliability in dynamic game states.
    - Bigger picture: Improves script robustness against timing issues or failures.
    """
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
    """
    Types the given quantity with random delays between keys, then presses Enter.
    - Helps understand: Simulates human typing to avoid detection.
    - Bigger picture: Enhances script stealth in automated environments.
    """
    try:
        for char in quantity:
            keyboard.press_and_release(char)
            time.sleep(random.uniform(MIN_TYPING_DELAY, MAX_TYPING_DELAY))  # Random delay per key
        keyboard.press_and_release('enter')
        print(f"Successfully typed '{quantity}' and pressed Enter.")
    except PermissionError:
        print("Error: Run as administrator/root for global keyboard access.")
        exit('Keyboard permission error')
    except Exception as e:
        print(f"Unexpected error: {e}")
        exit('Unexpected keyboard error')

def main():
    time.sleep(INITIAL_SLEEP)

    # Ensure RuneLite is focused once to allow keyboard input; cached in window_utils
    from modules.core.window_utils import focus_runelite_window
    focus_runelite_window()

    # Click reward chest (robust): try up to 3 times; each attempt waits up to 15 ticks for the
    # rewards/benefits widget to become clickable (to handle misclicks or UI lag).
    def open_rewards_chest(retries=3, timeout_ticks=15):
        for attempt in range(1, retries + 1):
            print(f"Opening rewards chest, attempt {attempt}/{retries}")
            click_gameobject(REWARD_CHEST_ID, REWARD_CHEST_ACTION, REWARD_CHEST_COORDS)

            tick_waited = 0
            while tick_waited < timeout_ticks:
                # Try to click the benefits child; if it succeeds, we're done
                try:
                    clicked = click_widget_child(BENEFITS_WIDGET_ID, child_index=BENEFITS_CHILD_INDEX)
                except Exception:
                    clicked = False

                if clicked:
                    print('Clicked benefits successfully')
                    return True

                # If the widget isn't yet available, wait one tick and try again
                wait_for_tick(1)
                tick_waited += 1

            print(f"Attempt {attempt} timed out after {timeout_ticks} ticks, retrying...")

        return False

    if not open_rewards_chest(retries=3, timeout_ticks=15):
        exit('Benefits failed')

    # Step 2: Get current states
    points = get_reward_points()
    abs_current = get_abs_current()
    ovl_current = get_ovl_current()
    print(f"Reward points: {points}")
    print(f"Current absorption doses: {abs_current}")
    print(f"Current overload doses: {ovl_current}")

    # Calculate needed quantities (can be 0)
    needed_abs = max(0, MAX_ABS - abs_current)
    needed_ovl = max(0, MAX_OVL - ovl_current)

    # Initialize quantities to buy
    abs_quantity = 0
    overload_quantity = 0

    # Step 3: Purchase logic - always attempt to top up if needed and points allow
    if points > MIN_POINTS_THRESHOLD and (needed_abs > 0 or needed_ovl > 0):
        total_cost = needed_abs * ABS_COST + needed_ovl * OVL_COST
        if points >= total_cost:
            # Ample points: Buy to max absorption and overload
            abs_quantity = needed_abs
            overload_quantity = needed_ovl
            print(f"Full buy: {abs_quantity} abs doses, {overload_quantity} ovl doses")
        else:
            # Limited points: Prioritize up to 4 absorption, then max overload possible
            abs_quantity = min(4, needed_abs)
            abs_cost = abs_quantity * ABS_COST
            if points >= abs_cost:
                remaining_points = points - abs_cost
                overload_quantity = min(needed_ovl, remaining_points // OVL_COST)
                print(f"Limited buy: {abs_quantity} abs doses, {overload_quantity} ovl doses")
            else:
                # Not enough even for absorption; try to buy as much overload as possible
                overload_quantity = min(needed_ovl, points // OVL_COST)
                print(f"Very limited buy: 0 abs doses, {overload_quantity} ovl doses")
    else:
        if points <= MIN_POINTS_THRESHOLD:
            print(f"Points <= {MIN_POINTS_THRESHOLD}, skipping purchase")
        else:
            print("No potions needed, skipping purchase")

    # Step 4: Buy absorption if needed (priority first)
    if abs_quantity > 0:
        if not wait_for_success(lambda: click_widget_child(ABS_BUY_X_WIDGET_ID, child_index=ABS_BUY_X_CHILD_INDEX, action=ABS_BUY_X_ACTION),
                                attempt_msg="Waiting to buy-x tab (absorption)"):
            exit('Absorption buy-x failed')

        print('Clicked absorption buy-x successfully')

        if not wait_for_success(lambda: check_widget(CHAT_WIDGET_ID),
                                attempt_msg="Waiting to open chat widget (absorption)"):
            exit('Absorption chat widget failed')

        type_quantity(str(abs_quantity))
        print('Typed absorption quantity successfully')
    else:
        print("Skipping absorption purchase")

    # Step 5: Buy overload if needed
    if overload_quantity > 0:
        if not wait_for_success(lambda: click_widget_child(OVL_BUY_X_WIDGET_ID, child_index=OVL_BUY_X_CHILD_INDEX, action=OVL_BUY_X_ACTION),
                                attempt_msg="Waiting to buy-x tab (overload)"):
            exit('Overload buy-x failed')

        print('Clicked overload buy-x successfully')

        if not wait_for_success(lambda: check_widget(CHAT_WIDGET_ID),
                                attempt_msg="Waiting to open chat widget (overload)"):
            exit('Overload chat widget failed')

        type_quantity(str(overload_quantity))
        print('Typed overload quantity successfully')
    else:
        print("Skipping overload purchase")

    keyboard.press_and_release('esc')
    # After buying, if we can afford at least one Absorption dose or we already
    # have absorption doses in storage, trigger the barrel withdrawal step.
    # Decide whether to trigger barrel withdraw. Use the values we already read
    # from the rewards UI earlier (abs_current, ovl_current) because the UI
    # may be closed after pressing Esc and re-reading the widget can fail.
    try:
        can_afford_abs = points >= ABS_COST
    except Exception:
        can_afford_abs = False
    try:
        can_afford_ovl = points >= OVL_COST
    except Exception:
        can_afford_ovl = False

    stored_abs = abs_current + abs_quantity
    stored_ovl = ovl_current + overload_quantity

    should_withdraw = (can_afford_abs or can_afford_ovl) or (stored_abs > 0) or (stored_ovl > 0)

    if should_withdraw:
        print(f"Should withdraw later (can_afford_abs={can_afford_abs}, can_afford_ovl={can_afford_ovl}, stored_abs={stored_abs}, stored_ovl={stored_ovl})")
    else:
        print("No withdraw needed: insufficient points and no stored doses.")

    # Return a summary so the caller can decide whether to withdraw and what changed
    return {
        'points': points,
        'stored_abs': stored_abs,
        'stored_ovl': stored_ovl,
        'abs_bought': abs_quantity,
        'ovl_bought': overload_quantity,
    }

if __name__ == "__main__":
    main()