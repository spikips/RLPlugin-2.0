import time
import random
import keyboard
from modules.object_data.game_object import click_gameobject
from modules.widgets.widget import check_widget, check_widget_text
from modules.utils.wait_for_tick import wait_for_tick
from modules.core.plugin_client import player
from potions import get_total_doses

# Configurable parameters
INITIAL_SLEEP = 0  # seconds
MAX_ATTEMPTS = 3  # 3 tries for both barrel click and widget check
MAX_TICKS = 10  # Max 10 ticks per attempt (~6 seconds)
MIN_TYPING_DELAY = 0.039  # seconds (lower bound for random delay)
MAX_TYPING_DELAY = 0.081  # seconds (upper bound for random delay)
OVERLOAD_BARREL_ID = "26279"
OVERLOAD_ACTION = "Take overload potion"
OVERLOAD_TILE = (2600, 3116)
OVERLOAD_DESIRED_DOSES = 72
ABSORPTION_BARREL_ID = "26280"
ABSORPTION_ACTION = "Take absorption potion"
ABSORPTION_TILE = (2600, 3117)
ABSORPTION_DESIRED_DOSES = 28
CHAT_WIDGET_ID = "10616875"


def get_stored_counts():
    """Try to read stored overload/absorption counts from the rewards widget.

    Returns (stored_abs, stored_ovl) where each is an int if readable,
    or (None, None) if the widget/text could not be read.
    """
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
    """
    Generic waiter: Retries a condition function until success or max attempts reached, with a tick-based timeout.
    - condition_func: A callable that returns True on success.
    - max_attempts: Maximum number of retry attempts (default: 3).
    - max_ticks: Maximum ticks to wait per attempt (default: 10, ~6 seconds).
    - attempt_msg: Message to log for each attempt.
    - Helps in understanding: Abstracts retry logic with tick-based timing for game synchronization.
    - Bigger picture: Ensures robust retry behavior while respecting game tick mechanics.
    """
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
    """
    Check if the player is within max_distance tiles of the target tile.
    Returns True if in range, False otherwise.
    - Helps in understanding: Uses Manhattan distance for simple proximity check.
    - Bigger picture: Prevents actions when player is out of range, avoiding failures.
    """
    player_data = player(location=True)
    if not player_data or 'data' not in player_data or 'location' not in player_data['data']:
        print("Failed to retrieve player location.")
        return False
    player_x = player_data['data']['location']['x']
    player_y = player_data['data']['location']['y']
    target_x, target_y = tile
    distance = abs(player_x - target_x) + abs(player_y - target_y)  # Manhattan distance
    if distance <= max_distance:
        print(f"Player is within {distance} tiles of target {tile}")
        return True
    print(f"Player is {distance} tiles away from target {tile}, too far (max {max_distance})")
    return False

def type_quantity(quantity: int):
    """
    Types the given quantity with random delays between keys, then presses Enter.
    - Converts quantity to string to iterate over characters.
    - Helps in understanding: Simulates human-like typing for stealth.
    - Bigger picture: Reduces risk of detection in automated environments.
    """
    try:
        quantity_str = str(quantity)  # Convert int to string for iteration
        for char in quantity_str:
            keyboard.press_and_release(char)
            time.sleep(random.uniform(MIN_TYPING_DELAY, MAX_TYPING_DELAY))  # Random delay per key
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
    """
    Withdraws a potion from the specified barrel, handling retries and chat widget.
    Returns True if successful and total doses meet desired after withdrawal, False otherwise.
    - Helps in understanding: Integrates proximity check and typing for full withdrawal flow, with post-check for sufficiency.
    - Bigger picture: Ensures potion levels are sufficient before proceeding, preventing under-prepared entry into NMZ.
    """
    if quantity <= 0:
        print(f"No need to withdraw {potion_name}: Already at or above desired doses.")
        return True

    # Record starting total to detect partial gains
    initial_total = get_total_doses(potion_name.lower())

    # Check player proximity to barrel
    if not check_player_proximity(tile, max_distance=20):
        print(f"Cannot withdraw {potion_name}: Player too far from barrel.")
        return False

    for attempt in range(MAX_ATTEMPTS):
        print(f"Attempting to withdraw {potion_name} ({quantity} doses), attempt {attempt + 1}/{MAX_ATTEMPTS}")
        # Step 1: Click the barrel
        if not click_gameobject(barrel_id, action, tile):
            print(f"Failed to click {potion_name} barrel on attempt {attempt + 1}")
            wait_for_tick(1)  # Wait to reset game state
            continue

        print(f"Clicked {potion_name} barrel successfully")
        
        # Step 2: Wait for chat widget
        if wait_for_success(lambda: check_widget(CHAT_WIDGET_ID),
                           max_attempts=1,  # Single attempt for widget check per barrel click
                           max_ticks=MAX_TICKS,
                           attempt_msg=f"Waiting for chat widget ({potion_name})"):
            print(f"Found chat widget for {potion_name}")
            # Read chat widget text to detect empty/placeholder messages from the barrel
            try:
                chat_text = check_widget_text(CHAT_WIDGET_ID) or ""
            except Exception:
                chat_text = ""

            # If the chat indicates the barrel is empty or out of doses, skip withdrawing
            empty_indicators = ['no doses', 'no potion', 'no potions', 'nothing left', 'out of', 'not enough', 'there are no']
            if any(ind in chat_text.lower() for ind in empty_indicators):
                print(f"Barrel appears empty or out of potions for {potion_name}: '{chat_text}'. Skipping withdraw.")
                return True

            print(f"Withdrawing {potion_name}")
            type_quantity(quantity)
            # Wait for inventory update
            wait_for_tick(2)
            # Check total doses after withdrawal
            new_total = get_total_doses(potion_name.lower())
            if new_total >= desired_doses:
                print(f"Withdrew {potion_name} successfully, total doses: {new_total}")
                return True
            if new_total > initial_total:
                gained = new_total - initial_total
                print(f"Partially withdrew {potion_name}: gained {gained} doses (total {new_total}), desired was {desired_doses}. Accepting partial withdraw.")
                return True
            # No increase; continue to next attempt
            print(f"No doses gained from this withdraw attempt for {potion_name} (total still {new_total}). Retrying if attempts remain.")
        
        print(f"Chat widget not found for {potion_name} after attempt {attempt + 1}")
        wait_for_tick(1)  # Wait to reset game state before retrying

    # After all attempts, check if we managed to gain any doses at all
    final_total = get_total_doses(potion_name.lower())
    if final_total > initial_total:
        gained = final_total - initial_total
        print(f"After attempts, partially withdrew {potion_name}: gained {gained} doses (total {final_total}).")
        return True

    print(f"Failed to withdraw {potion_name} after {MAX_ATTEMPTS} attempts and no doses gained.")
    return False

def main(stored_abs=None, stored_ovl=None):
    """Main withdraw entry. If stored_abs/stored_ovl are provided they will be
    used instead of attempting to read the rewards widget (which may be closed).
    """
    time.sleep(INITIAL_SLEEP)

    # Use provided stored counts if available; otherwise try to read them
    if stored_abs is None or stored_ovl is None:
        stored_abs_read, stored_ovl_read = get_stored_counts()
        if stored_abs is None:
            stored_abs = stored_abs_read
        if stored_ovl is None:
            stored_ovl = stored_ovl_read

    if stored_abs is not None and stored_ovl is not None:
        print(f"Stored counts from rewards UI (or caller): Absorption={stored_abs}, Overload={stored_ovl}")
    else:
        print("Stored counts unknown; proceeding with inventory-based withdrawals")

    # Calculate and withdraw Overload if needed and if stored_ovl isn't explicitly 0
    current_overload = get_total_doses("overload")
    overload_needed = max(0, OVERLOAD_DESIRED_DOSES - current_overload)
    if stored_ovl == 0:
        print("Stored overload count is 0; skipping overload barrel withdraw.")
        overload_needed = 0

    if overload_needed > 0:
        # Use stored_ovl as available doses to withdraw if provided; otherwise attempt a single withdraw sequence
        available_stored = stored_ovl if isinstance(stored_ovl, int) else None
        print(f"Attempting to withdraw overload: need {overload_needed} doses, stored available: {available_stored}")

        # Loop until we've reached desired doses or stored is exhausted or no progress
        while current_overload < OVERLOAD_DESIRED_DOSES:
            if available_stored is not None and available_stored <= 0:
                print("No stored overload doses remaining; stopping withdraw attempts.")
                break

            to_withdraw = OVERLOAD_DESIRED_DOSES - current_overload
            if available_stored is not None:
                to_withdraw = min(to_withdraw, available_stored)

            print(f"Withdrawing overload, trying to get {to_withdraw} doses now (current total {current_overload})")
            prev_total = current_overload
            success = withdraw_potion(OVERLOAD_BARREL_ID, OVERLOAD_ACTION, OVERLOAD_TILE, to_withdraw, "Overload", OVERLOAD_DESIRED_DOSES)

            # Recompute totals and adjust available stored count by actual gained amount
            current_overload = get_total_doses("overload")
            gained = current_overload - prev_total
            if available_stored is not None:
                # Deduct the actual gained doses from stored estimate
                available_stored = max(0, available_stored - gained)

            if gained <= 0:
                print("No doses gained from withdraw attempt; stopping further attempts for overload.")
                break

            if current_overload >= OVERLOAD_DESIRED_DOSES:
                print(f"Reached desired overload doses: {current_overload}")
                break

        if current_overload >= OVERLOAD_DESIRED_DOSES:
            print("Overload handling complete, proceeding to Absorption")
        else:
            print("Overload withdraw finished without reaching full desired doses.")
    else:
        print("No overload withdraw necessary.")

    # Wait for inventory to update
    wait_for_tick(1)

    # Calculate and withdraw Absorption if needed and if stored_abs isn't explicitly 0
    current_absorption = get_total_doses("absorption")
    absorption_needed = max(0, ABSORPTION_DESIRED_DOSES - current_absorption)
    if stored_abs == 0:
        print("Stored absorption count is 0; skipping absorption barrel withdraw.")
        absorption_needed = 0

    if absorption_needed > 0:
        available_stored_abs = stored_abs if isinstance(stored_abs, int) else None
        print(f"Attempting to withdraw absorption: need {absorption_needed} doses, stored available: {available_stored_abs}")

        while current_absorption < ABSORPTION_DESIRED_DOSES:
            if available_stored_abs is not None and available_stored_abs <= 0:
                print("No stored absorption doses remaining; stopping withdraw attempts.")
                break

            to_withdraw = ABSORPTION_DESIRED_DOSES - current_absorption
            if available_stored_abs is not None:
                to_withdraw = min(to_withdraw, available_stored_abs)

            print(f"Withdrawing absorption, trying to get {to_withdraw} doses now (current total {current_absorption})")
            prev_total = current_absorption
            success = withdraw_potion(ABSORPTION_BARREL_ID, ABSORPTION_ACTION, ABSORPTION_TILE, to_withdraw, "Absorption", ABSORPTION_DESIRED_DOSES)

            current_absorption = get_total_doses("absorption")
            gained = current_absorption - prev_total
            if available_stored_abs is not None:
                available_stored_abs = max(0, available_stored_abs - gained)

            if gained <= 0:
                print("No doses gained from withdraw attempt; stopping further attempts for absorption.")
                break

            if current_absorption >= ABSORPTION_DESIRED_DOSES:
                print(f"Reached desired absorption doses: {current_absorption}")
                break

        if current_absorption >= ABSORPTION_DESIRED_DOSES:
            print("Absorption handling complete, script finished")
        else:
            print("Absorption withdraw finished without reaching full desired doses.")
    else:
        print("No absorption withdraw necessary, script finished.")

# time.sleep(3)
if __name__ == "__main__":
    main()