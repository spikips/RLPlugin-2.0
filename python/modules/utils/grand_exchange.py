# modules/utils/grand_exchange.py
"""
Grand Exchange automation module for RuneLite OSRS bot.
All functions in one file. Plain ASCII only - compatible with older Python.
Focus clicks: 4 (1st) -> 10 (2nd) -> 25 (3rd+).
When inventory full: ESC + banker + deposit inventory + ESC + reopen GE + clean pending offers.
"""

from typing import Any, Dict, Optional
import keyboard

# Core imports
from modules.core.mouse_control import move, scroll
from modules.core.plugin_client import _default_client
from modules.core.window_utils import focus_runelite_window, runelite_window
from modules.widgets.widget import check_widget, click_widget_child, click_widget_by_name
from modules.npc_data.click_npc import click_closest_npc
from modules.player_data.wait_till_character_stops_moving import wait_till_character_stopped_moving
from modules.utils.wait_for_tick import wait_for_next_tick, wait_for_tick
from modules.utils.inventory import is_inventory_full


def grand_exchange() -> Optional[Dict[str, Any]]:
    """Clean grand exchange data (no 'data' wrapper)."""
    response = _default_client.send_request('grand_exchange', {})
    if response and isinstance(response, dict) and 'data' in response:
        return response['data']
    return response


def is_grand_exchange_open() -> bool:
    """Returns True if the Grand Exchange main interface is open."""
    return check_widget('30474242', sprite_id=None, hidden=None, child_index=11)


def open_grand_exchange(max_attempts=10) -> bool:
    """Clicks closest Grand Exchange clerk and waits for interface to open."""
    print("Attempting to open Grand Exchange...")
    for i in range(max_attempts):
        if not click_closest_npc('grand exchange clerk', option='exchange', max_attempts=5):
            wait_for_next_tick()
            continue

        if wait_till_character_stopped_moving():
            wait_for_next_tick(2)
            if is_grand_exchange_open():
                print("Grand Exchange opened successfully.")
                return True

        wait_for_next_tick()

    print("Failed to open Grand Exchange after {} attempts.".format(max_attempts))
    exit("Failed to click npc (grand exchange clerk)")
    return False


def _clean_pending_offers():
    """After reopening GE (or at start of buy), clean any lingering offers.
    This fixes the issue you saw: after banking the interface still had old offer state."""
    print("Cleaning any pending GE offers...")
    offers_data = grand_exchange()
    cleaned = 0
    for offer in offers_data.get('offers', []):
        if not offer.get('isEmpty', True):
            state = offer.get('state')
            progress = offer.get('progressPercent', 0)
            complete = offer.get('isComplete', False)
            item_name = offer.get('itemName', '')

            print("Found pending offer: {} - {} ({}%)".format(item_name, state, progress))

            if complete or progress >= 95.0 or state in ('BOUGHT', 'COMPLETED'):
                _collect_to_inventory()
            else:
                _abort_and_collect()
            cleaned += 1
    if cleaned == 0:
        print("No pending offers to clean.")
    else:
        print("Cleaned {} offers.".format(cleaned))
    wait_for_next_tick(3)


def _click_buy_offer() -> bool:
    """Click the 'Buy' button (widget 30474247, child 3)."""
    for i in range(5):
        if click_widget_child('30474247', sprite_id=None, hidden=None, child_index=3):
            wait_for_next_tick(2)
            return True
        wait_for_next_tick()
    exit("Failed to click dialogue option (create buy offer) via child")
    return False


def _type_item_and_select(item_name):
    """Type item name, wait, then retry hover-scroll-click up to 10 times.
    Hover at canvas 271,529 + scroll down 2x before each attempt (for long lists like knife)."""
    print("Typing item: {}".format(item_name))
    keyboard.write(item_name)
    wait_for_next_tick(2)

    for retry in range(10):
        print("Search retry {}/10 for '{}'".format(retry + 1, item_name))
        # Hover at canvas 271,529 (convert to screen)
        x, y = runelite_window(0, 0)
        
        move(271 + x, 424 + y, fast=True)
        wait_for_next_tick(0.3)
        # Scroll down 2 times
        scroll(-1)
        wait_for_next_tick(0.2)
        scroll(-1)
        wait_for_next_tick(0.2)
        # Try select with your canvas restriction
        success = click_widget_by_name(item_name, action='Select', exact_match=True, canvas=(0, 345, 514, 139))
        if success:
            wait_for_next_tick(2)
            return True

    exit("Failed to select item '{}' after 10 retries".format(item_name))
    return False


def _focus_quantity_field(attempt=0) -> bool:
    """Click the quantity/price panel (widget 30474266, child 13).
    attempt=0 (1st) -> 4 clicks
    attempt=1 (2nd) -> 10 clicks
    attempt>=2 (3rd+) -> 25 clicks"""
    if attempt == 0:
        clicks = 4
    elif attempt == 1:
        clicks = 10
    else:
        clicks = 25
    for i in range(clicks):
        if i == clicks - 1 and not click_widget_child('30474266', sprite_id=None, hidden=None, child_index=13):
            return False
        click_widget_child('30474266', sprite_id=None, hidden=None, child_index=13)
    return True


def _enter_custom_quantity(quantity):
    """If quantity > 1, click 'Enter quantity' and type it."""
    if quantity <= 1:
        return True

    for i in range(5):
        if click_widget_child('30474266', sprite_id=None, hidden=None, child_index=7):
            break
        wait_for_next_tick()
    else:
        exit("Failed to click dialogue option (enter quantity) via child")

    wait_for_next_tick(2)
    keyboard.write(str(quantity))
    keyboard.press_and_release('enter')
    wait_for_next_tick(2)
    return True


def _confirm_offer() -> bool:
    """Click Confirm Offer (widget 30474270, child 3)."""
    for i in range(5):
        if click_widget_child('30474270', sprite_id=None, hidden=None, child_index=3, clicks=2, rand_x=3, rand_y=3):
            wait_for_next_tick(3)
            return True
        wait_for_next_tick()
    exit("Failed to click dialogue option (confirm) via child")
    return False


def _collect_to_inventory() -> bool:
    """Collect completed offer to inventory (widget 30474246, child 0)."""
    for i in range(5):
        if click_widget_child('30474246', sprite_id=None, hidden=None, child_index=0):
            wait_for_next_tick(3)
            print("Collected offer to inventory.")
            return True
        wait_for_next_tick()
    exit("Failed to click dialogue option (collect to inventory) via child")
    return False


def _empty_inventory_to_bank():
    """When inventory full: ESC + banker + deposit inventory + ESC + reopen GE + clean offers."""
    print("Inventory full - banking everything...")
    keyboard.press_and_release('esc')
    wait_for_next_tick(3)

    for i in range(10):
        if click_closest_npc('banker', option='bank', max_attempts=5):
            wait_for_next_tick(2)
            break
        if i == 9:
            exit("Failed to click npc (banker)")

    for i in range(5):
        if click_widget_child('786473', sprite_id=None, hidden=None, child_index=14, right_click=False, action=None):
            break
        wait_for_next_tick()
        if i == 4:
            exit("Failed to click dialogue option (deposit inventory) via child")

    keyboard.press_and_release('esc')
    wait_for_next_tick(2)

    open_grand_exchange()
    _clean_pending_offers()   # <-- this fixes your issue
    print("Banked inventory - GE reopened and cleaned.")


def _abort_and_collect() -> bool:
    """Abort offer then collect."""
    print("Offer not completed - aborting...")
    for i in range(5):
        if click_widget_child('30474247', sprite_id=None, hidden=None, child_index=2, action="abort offer"):
            wait_for_tick(3)
            return _collect_to_inventory()
        wait_for_next_tick()
    exit("Failed to click dialogue option (abort offer) via child")
    return False


def buy_item(item_name, quantity=1, max_retries=3):
    """
    Full buy flow with automatic retry if offer fails to complete.
    Normal attempt: focus clicks 4 times.
    Retry attempt: focus clicks 10 times.
    3rd attempt: focus clicks 25 times.
    No wait after confirm_offer.
    """
    print("Starting buy: {}x {}".format(quantity, item_name))

    for attempt in range(max_retries + 1):
        if attempt > 0:
            print("--- Retry attempt {}/{} ---".format(attempt + 1, max_retries + 1))

        if not is_grand_exchange_open():
            open_grand_exchange()
        _clean_pending_offers()   # <-- always start clean

        _click_buy_offer()
        _type_item_and_select(item_name)
        
        focused = _focus_quantity_field(attempt)
        if not focused:
            print("Focus quantity field failed after {} attempts - skipping buy.".format(4 if attempt == 0 else 10 if attempt == 1 else 25))
            if attempt == max_retries:
                break
            wait_for_tick(3)
            continue
        
        _enter_custom_quantity(quantity)
        _confirm_offer()

        offers_data = grand_exchange()
        item_lower = item_name.lower()

        for offer in offers_data.get('offers', []):
            if offer.get('itemName', '').lower() == item_lower and not offer.get('isEmpty', True):
                state = offer.get('state')
                progress = offer.get('progressPercent', 0)
                complete = offer.get('isComplete', False)

                print("Offer status: {} | Progress: {}% | Complete: {}".format(state, progress, complete))

                if complete or progress >= 95.0 or state in ('BOUGHT', 'COMPLETED'):
                    _collect_to_inventory()
                    print("Buy completed successfully!")
                    return offers_data
                else:
                    _abort_and_collect()
                    break
        else:
            print("Offer not found in response - attempting collect anyway")
            _collect_to_inventory()

        if attempt == max_retries:
            print("All retry attempts failed - skipping buy.")
            break

        wait_for_tick(3)

    return grand_exchange()


def buy_shopping_list():
    focus_runelite_window()
    """Buy every item on your full shopping list in one go.
    Uses exact names and quantities you listed.
    Run this function to buy everything."""
    shopping_list = [
        # ("ring of wealth (5)", 20),
        # ("amulet of glory(6)", 10),
        # ("combat bracelet(6)", 5),
        # ("ring of dueling(8)", 100),
        # ("games necklace(8)", 10),
        # ("skills necklace(6)", 10),
        # ("necklace of passage(5)", 5),
        # ("dragon bones", 3500),
        # ("burning amulet(5)", 40),
        # ("stamina potion(4)", 30),
        # ("summer pie", 200),
        # ("air rune", 20000),
        # ("water rune", 20000),
        # ("earth rune", 20000),
        # ("fire rune", 20000),
        # ("mind rune", 5000),
        # ("chaos rune", 5000),
        # ("law rune", 5000),
        # ("staff of air", 1),
        # ("staff of fire", 1),
        # ("camelot teleport", 10),
        # ("falador teleport", 20),
        # ("lumbridge teleport", 10),
        # ("varrock teleport", 10),
        # ("prayer potion(4)", 200),
        # ("monk's robe", 1),
        # ("monk's robe top", 1),
        # ("ancient cloak", 1),
        # ("honourable blessing", 1),
        # ("candle", 1),
        # ("clay", 6),
        # ("copper ore", 4),
        # ("iron ore", 2),
        # ("redberry pie", 1),
        # ("iron bar", 2),
        # ("steel pickaxe", 1),
        # ("black bead", 1),
        # ("white bead", 1),
        # ("red bead", 1),
        # ("yellow bead", 1),
        # ("onion", 1),
        # ("cooked meat", 1),
        # ("eye of newt", 2),
        # ("cheese", 1),
        # ("leather gloves", 1),
        # ("knife", 1),



        # for slayer

        ("holy sandals", 1)
        ("waterskin(4)", 40),
        ("antidote++(4)", 10),
        ("Amulet of glory(6)", 40),
        ("zombie axe", 1),
        ("antler guard", 1),
        ("glacial temotli", 1),
        ("dwarf cannon set", 1),
        ("steel cannonball", 10000),
        ("nature rune", 1000),
        ("games necklace(8)", 40),
        ("salve graveyard teleport", 50),
        ("Fenkenstrain's castle teleport", 30),
        ("camelot teleport", 20),
        ("barrows teleport", 20)
    ]

    print("Starting shopping list - {} items".format(len(shopping_list)))
    for name, qty in shopping_list:
        if is_inventory_full():
            _empty_inventory_to_bank()
        buy_item(name, qty, max_retries=2)
    print("Shopping list finished.")




if __name__ == "__main__":
    print("Grand Exchange module ready.")
    # Test the full list (uncomment to run):
    buy_shopping_list()