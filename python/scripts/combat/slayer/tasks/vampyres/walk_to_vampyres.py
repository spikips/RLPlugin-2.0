from modules.utils.click_minimap_tile import click_minimap_tile
from modules.player_data.tile_change import wait_for_tile_change
from modules.utils.wait_for_tick import wait_for_tick, wait_for_next_tick
from modules.widgets.widget import click_widget, click_widget_child

from modules.utils.inventory import click_inventory
from modules.widgets.widget import click_widget_child
from modules.player_data.wait_till_character_stops_moving import wait_till_character_stopped_moving

from modules.utils.hop import hop_to_random_world
from modules.banking.bank_castlewars import bank_castlewars
from modules.utils.check_players import check_for_players
from scripts.combat.slayer.slayer_gear import get_target_gear


def go_to_bank():
    """Go to bank and get target gear and inventory."""
    target_gear = get_target_gear()

    target_inventory = {
    "Prayer potion": 6,
    "Games necklace": 1,
    "Amulet of glory": 1,
    "Ring of dueling": 2,
    "Cannon barrels": 1,
    "Cannon furnace": 1,
    "Cannon base": 1,
    "Cannon stand": 1,
    "Steel cannonball": "all",
    "Coins": 1000,
    "Fenkenstrain's castle teleport": 1
    }

    bank_castlewars(target_gear=target_gear, target_inventory=target_inventory)


def walk_to_vampyres():
    """Walk to the vampyres location."""
    for i in range(5):
        if click_inventory("fenkenstrain's castle teleport", action='break', hover_only=False):
            wait_for_tile_change()
            wait_for_next_tick(2)
            break
        wait_for_next_tick()
        if i == 4:
            exit("Failed to click inventory item (Fenkenstrain's castle teleport, Break)")

    # 2
    for i in range(10):
        if click_minimap_tile(3558, 3504, rand_x=2, rand_y=2, target_zoom=2.0):
            print("clicked minimap tile (3558, 3504)")
            if wait_till_character_stopped_moving():
                break
        wait_for_next_tick()
        if i == 9:
            exit("Failed to click minimap tile (3558, 3504)")

    # 6
    for i in range(10):
        if click_minimap_tile(3577, 3479, rand_x=2, rand_y=2, target_zoom=2.0):
            print("clicked minimap tile (3577, 3479)")
            # parent id: 35913791
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

            # 5
            # parent id: 35913791
            for i in range(5):
                if click_widget_child('35913795', sprite_id=None, hidden=None, child_index=3, right_click=False, action=None):
                    break
                wait_for_next_tick()
                if i == 4:
                    exit("Failed to click dialogue option (inventory) via child")

            if wait_till_character_stopped_moving():
                break
        wait_for_next_tick()
        if i == 9:
            exit("Failed to click minimap tile (3577, 3479)")

    # 7
    for i in range(10):
        if click_minimap_tile(3592, 3480, rand_x=2, rand_y=2, target_zoom=2.0):
            print("clicked minimap tile (3592, 3480)")
            if wait_till_character_stopped_moving():
                break
        wait_for_next_tick()
        if i == 9:
            exit("Failed to click minimap tile (3592, 3480)")


def hop_if_players_nearby():
    """Hop worlds if players are detected nearby."""
    hop_tile =  (3592, 3480, 0)
    stand_tile =  (3592, 3480, 0)

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
    walk_to_vampyres()
    hop_if_players_nearby()


if __name__ == "__main__":
    run()
