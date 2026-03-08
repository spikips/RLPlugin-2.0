from modules.player_data.tile_change import wait_for_tile_change
from modules.player_data.wait_till_character_stops_moving import wait_till_character_stopped_moving
from modules.utils import wait_for_tick
from modules.utils.click_minimap_tile import click_minimap_tile
from modules.utils.automatic_scripting.small_functions import click_lowest_necklace_of_passage
from modules.widgets.widget import click_widget, click_widget_child
from scripts.combat.moss_giant.ground_items import wait_for_next_tick

from modules.utils.hop import hop_to_random_world
from modules.banking.bank_castlewars import bank_castlewars
from modules.utils.check_players import check_for_players
from scripts.combat.slayer.slayer_gear import get_target_gear


def go_to_bank():
    """Go to bank and get target gear and inventory."""
    target_gear = get_target_gear()

    target_inventory = {
    "Prayer potion": 7,
    "Games necklace": 1,
    "Amulet of glory": 1,
    "Ring of dueling": 2,
    "Cannon barrels": 1,
    "Cannon furnace": 1,
    "Cannon base": 1,
    "Cannon stand": 1,
    "Steel cannonball": "all",
    "Necklace of passage": 1
    }

    bank_castlewars(target_gear=target_gear, target_inventory=target_inventory)


def walk_to_hobgoblins():
    """Walk to the hobgoblins location."""
    for i in range(5):
        if click_lowest_necklace_of_passage(action='Rub'):
            wait_for_next_tick()
            break
        wait_for_next_tick()
        if i == 4:
            exit("Failed to click jewelry: Necklace of passage(1) (Rub)")

    # 2
    for i in range(5):
        if click_widget_child('14352385', sprite_id=None, hidden=False, child_index=2, right_click=False, action=None):
            wait_for_tile_change()
            break
        wait_for_next_tick()
        if i == 4:
            exit("Failed to click dialogue option (the outpost) via child")

    # 3
    for i in range(10):
        if click_minimap_tile(2447, 3363, rand_x=2, rand_y=2, target_zoom=2.0):
            print("clicked minimap tile (2447, 3363)")
            for i in range(5):
                if click_widget_child('35913797', sprite_id=None, hidden=None, child_index=5, right_click=False, action=None):
                    break
                wait_for_next_tick()
                if i == 4:
                    exit("Failed to click dialogue option (prayer) via child")

            # 4
            for i in range(5):
                if click_widget('35454999', action='activate', hidden=False, right_click=False, rand_x=0, rand_y=0, clicks=1, sleep_interval=(0, 0)):
                    break
                wait_for_next_tick()
                if i == 4:
                    exit("Failed to activate prayer (protect from melee)")
            if wait_till_character_stopped_moving():
                break
        wait_for_next_tick()
        if i == 9:
            exit("Failed to click minimap tile (2447, 3363)")

    # 5
    # parent id: 35913791
    for i in range(5):
        if click_widget_child('35913795', sprite_id=None, hidden=None, child_index=3, right_click=False, action=None):
            break
        wait_for_next_tick()
        if i == 4:
            exit("Failed to click dialogue option (inventory) via child")


def hop_if_players_nearby():
    """Hop worlds if players are detected nearby."""
    hop_tile =  (2447, 3363, 0)
    stand_tile =  (2445, 3364, 0)

    # hop until empty world
    max_hop_attempts = 15  # Safety limit to avoid infinite hopping
    for hop_attempt in range(max_hop_attempts):
        print(f"Checking for nearby players (attempt {hop_attempt + 1}/{max_hop_attempts})...")
        
        players_detected = check_for_players(radius=10, max_wait_ticks=2)
        
        if not players_detected:
            print("No players detected in 10 tile radius -> safe spot")
            break

        click_minimap_tile(hop_tile[0], hop_tile[1], target_zoom=2.0)
        wait_till_character_stopped_moving(required_idle_ticks=2)
        wait_for_next_tick(8)


        print("Players detected -> hopping to new P2P world")
        if hop_to_random_world('p2p'):
            print("hopped, rechecking")
            wait_for_tick(3)
            continue

        players_detected = check_for_players(radius=10, max_wait_ticks=2)

        if not players_detected:
            click_minimap_tile(stand_tile[0], stand_tile[1], target_zoom=2.0)
            wait_till_character_stopped_moving(required_idle_ticks=2)
            break


def run():
    """Execute the main sequence: go to bank, walk to location, and check for players."""
    go_to_bank()
    walk_to_hobgoblins()
    hop_if_players_nearby()


if __name__ == "__main__":
    run()
