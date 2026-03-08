import time
from modules.core.plugin_client import gear, stats
from modules.fetch_data.fetch_bank_items import fetch_bank_items
from modules.object_data.game_object import click_gameobject
from modules.player_data.tile_change import wait_for_tile_change, wait_until_at_tile
from modules.player_data.wait_till_character_stops_moving import wait_till_character_stopped_moving
from modules.utils.automatic_scripting.small_functions import click_lowest_games_necklace
from modules.utils.camera import camera
from modules.utils.click_minimap_tile import click_minimap_tile
from modules.utils.click_tile import click_tile
from modules.utils.inventory import click_inventory
from modules.utils.wait_for_tick import wait_for_next_tick, wait_for_tick
from modules.widgets.widget import click_widget, click_widget_child


from modules.utils.hop import hop_to_random_world
from modules.banking.bank_castlewars import bank_castlewars
from modules.utils.check_players import check_for_players
from scripts.combat.slayer.slayer_gear import get_target_gear


def go_to_bank():
    """Go to bank and get target gear and inventory. Remove any base weapons and add Turoth-specific weapons."""
    target_gear = get_target_gear()

    print("Setting up Turoth-specific weapons...")

    # Remove ANY weapons that might be in the list
    weapons_to_remove = ["Glacial temotli", "Brine sabre", "Zombie axe", "Leaf-bladed sword", "Leaf-bladed battleaxe", "Antler guard"]
    for weapon in weapons_to_remove:
        while weapon in target_gear:
            target_gear.remove(weapon)
            print(f"Removed {weapon}")

    # Get current Attack level
    player_stats = stats()["data"]
    attack_level = player_stats.get("Attack", {}).get("level", 1)
    print(f"Detected Attack level: {attack_level}")

    # Helper to check if item is equipped or in bank
    def item_available(item_name: str) -> bool:
        equipped = gear()["data"].keys()
        if item_name in equipped:
            return True
        return fetch_bank_items([(item_name, 1)])

    # Add Turoth-specific weapons based on Attack level
    weapon_added = False

    if attack_level >= 65:
        # Prefer battleaxe (2H) at 65+
        if item_available("Leaf-bladed battleaxe"):
            target_gear.append("Leaf-bladed battleaxe")
            target_gear.append("Antler guard")
            print("-> Added: Leaf-bladed battleaxe + Antler guard (65+ Attack)")
            weapon_added = True
        # Fallback to sword if no battleaxe
        elif item_available("Leaf-bladed sword"):
            target_gear.append("Leaf-bladed sword")
            target_gear.append("Antler guard")
            print("-> No battleaxe found, added: Leaf-bladed sword + Antler guard")
            weapon_added = True

    elif attack_level >= 50:
        # 50–64: only sword is possible
        if item_available("Leaf-bladed sword"):
            target_gear.append("Leaf-bladed sword")
            target_gear.append("Antler guard")
            print("-> Added: Leaf-bladed sword + Antler guard (50–64 Attack)")
            weapon_added = True

    # Safety check
    if not weapon_added:
        exit("No suitable leaf-bladed weapon available or Attack level too low for Turoth task")

    target_inventory = {
        "Prayer potion": 8,
        "Amulet of glory": 1,
        "Ring of dueling": 2,
        "camelot teleport": 1,
        "nature rune": 200,
        "fire rune": 1000
    }
    bank_castlewars(target_gear=target_gear, target_inventory=target_inventory)


def walk_to_turoth():
    """Walk to the turoth location."""
    # 1
    # Inventory item click: Camelot teleport -> Camelot
    for i in range(5):
        if click_inventory('camelot teleport', action='camelot', hover_only=False):
            wait_for_tile_change()
            wait_for_next_tick(2)
            break
        wait_for_next_tick()
        if i == 4:
            exit("Failed to click inventory item (Camelot teleport, Camelot)")

    # 2
    # parent id: 35913752
    for i in range(5):
        if click_widget_child('35913752', sprite_id=None, hidden=None, child_index=1, right_click=False, action=None):
            break
        wait_for_next_tick()
        if i == 4:
            exit("Failed to click dialogue option (look north) via child")

    # 3
    for i in range(10):
        if click_minimap_tile(2741, 3510, rand_x=1, rand_y=1, target_zoom=2.0):
            print("clicked minimap tile (2741, 3510)")
            if wait_till_character_stopped_moving(required_idle_ticks=2):
                break
        wait_for_next_tick()
        if i == 9:
            exit("Failed to click minimap tile (2741, 3510)")

    # 4
    for i in range(10):
        if click_minimap_tile(2742, 3525, rand_x=1, rand_y=1, target_zoom=2.0):
            print("clicked minimap tile (2742, 3525)")
            if wait_till_character_stopped_moving(required_idle_ticks=2):
                break
        wait_for_next_tick()
        if i == 9:
            exit("Failed to click minimap tile (2742, 3525)")

    # 5
    for i in range(10):
        if click_minimap_tile(2724, 3543, rand_x=1, rand_y=1, target_zoom=2.0):
            print("clicked minimap tile (2724, 3543)")
            if wait_till_character_stopped_moving(required_idle_ticks=2):
                break
        wait_for_next_tick()
        if i == 9:
            exit("Failed to click minimap tile (2724, 3543)")

    # 6
    for i in range(10):
        if click_minimap_tile(2692, 3559, rand_x=1, rand_y=1, target_zoom=2.0):
            print("clicked minimap tile (2692, 3559)")
            if wait_till_character_stopped_moving(required_idle_ticks=2):
                break
        wait_for_next_tick()
        if i == 9:
            exit("Failed to click minimap tile (2692, 3559)")

    # 7
    for i in range(10):
        if click_minimap_tile(2661, 3570, rand_x=1, rand_y=1, target_zoom=2.0):
            print("clicked minimap tile (2661, 3570)")
            if wait_till_character_stopped_moving(required_idle_ticks=2):
                break
        wait_for_next_tick()
        if i == 9:
            exit("Failed to click minimap tile (2661, 3570)")

    # 8
    for i in range(10):
        if click_minimap_tile(2672, 3603, rand_x=1, rand_y=1, target_zoom=2.0):
            print("clicked minimap tile (2672, 3603)")
            if wait_till_character_stopped_moving(required_idle_ticks=2):
                break
        wait_for_next_tick()
        if i == 9:
            exit("Failed to click minimap tile (2672, 3603)")

    # 9
    for i in range(10):
        if click_minimap_tile(2704, 3613, rand_x=1, rand_y=1, target_zoom=2.0):
            print("clicked minimap tile (2704, 3613)")
            if wait_till_character_stopped_moving(required_idle_ticks=2):
                break
        wait_for_next_tick()
        if i == 9:
            exit("Failed to click minimap tile (2704, 3613)")

    # 10
    for i in range(10):
        if click_minimap_tile(2739, 3616, rand_x=1, rand_y=1, target_zoom=2.0):
            print("clicked minimap tile (2739, 3616)")
            if wait_till_character_stopped_moving(required_idle_ticks=2):
                break
        wait_for_next_tick()
        if i == 9:
            exit("Failed to click minimap tile (2739, 3616)")

    # 11
    for i in range(10):
        if click_minimap_tile(2772, 3615, rand_x=1, rand_y=1, target_zoom=2.0):
            print("clicked minimap tile (2772, 3615)")
            if wait_till_character_stopped_moving(required_idle_ticks=2):
                break
        wait_for_next_tick()
        if i == 9:
            exit("Failed to click minimap tile (2772, 3615)")

    for i in range(10):
        if click_minimap_tile(2787, 3613, rand_x=2, rand_y=2, target_zoom=2.0):
            print("clicked minimap tile (2787, 3613)")
            if wait_till_character_stopped_moving(required_idle_ticks=2):
                break
        wait_for_next_tick()
        if i == 9:
            exit("Failed to click minimap tile (2787, 3613)")

    # 12
    for i in range(10):
        if click_minimap_tile(2793, 3613, rand_x=1, rand_y=1, target_zoom=2.0):
            print("clicked minimap tile (2793, 3613)")
            # 13
            for i in range(3):
                if camera(pitch=281, yaw=1693, zoom=313, speed=10):
                    break
                if i == 2:
                    exit("Failed to set camera")
            if wait_till_character_stopped_moving(required_idle_ticks=2):
                break
        wait_for_next_tick()
        if i == 9:
            exit("Failed to click minimap tile (2793, 3613)")


    # 14
    # Object click: cave entrance -> Enter
    for i in range(5):
        if click_gameobject("2123", 'Enter', tile=(2798, 3615), radius=20):
            wait_until_at_tile(2808, 10002, radius=2)
            break
        wait_for_next_tick()
        if i == 4:
            exit("Failed to click object (cave entrance, Enter)")

    # 15
    for i in range(10):
        if click_minimap_tile(2790, 10031, rand_x=1, rand_y=1, target_zoom=2.0):
            print("clicked minimap tile (2790, 10031)")
            if wait_till_character_stopped_moving(required_idle_ticks=2):
                break
        wait_for_next_tick()
        if i == 9:
            exit("Failed to click minimap tile (2790, 10031)")

    # 16
    for i in range(10):
        if click_minimap_tile(2762, 10013, rand_x=1, rand_y=1, target_zoom=2.0):
            print("clicked minimap tile (2762, 10013)")
            if wait_till_character_stopped_moving(required_idle_ticks=2):
                break
        wait_for_next_tick()
        if i == 9:
            exit("Failed to click minimap tile (2762, 10013)")

    # 18
    for i in range(10):
        if click_minimap_tile(2740, 10011, rand_x=1, rand_y=1, target_zoom=2.0):
            print("clicked minimap tile (2740, 10011)")
            if wait_till_character_stopped_moving(required_idle_ticks=2):
                break
        wait_for_next_tick()
        if i == 9:
            exit("Failed to click minimap tile (2740, 10011)")

    # 19
    for i in range(10):
        if click_minimap_tile(2719, 10028, rand_x=1, rand_y=1, target_zoom=2.0):
            print("clicked minimap tile (2719, 10028)")
            if wait_till_character_stopped_moving(required_idle_ticks=2):
                break
        wait_for_next_tick()
        if i == 9:
            exit("Failed to click minimap tile (2719, 10028)")

    # 20
    for i in range(10):
        if click_minimap_tile(2723, 10002, rand_x=1, rand_y=1, target_zoom=2.0):
            print("clicked minimap tile (2723, 10002)")
            for i in range(3):
                if camera(pitch=423, yaw=1763, zoom=313, speed=10):
                    break
                if i == 2:
                    exit("Failed to set camera")
            if wait_till_character_stopped_moving(required_idle_ticks=2):
                break
        wait_for_next_tick()
        if i == 9:
            exit("Failed to click minimap tile (2723, 10002)")




def hop_if_players_nearby():
    """Hop worlds if players are detected nearby."""
    hop_tile =  (2723, 10002, 0)
    stand_tile =  (2723, 10002, 0)

    # hop until empty world
    max_hop_attempts = 15  # Safety limit to avoid infinite hopping
    for hop_attempt in range(max_hop_attempts):
        print(f"Checking for nearby players (attempt {hop_attempt + 1}/{max_hop_attempts})...")
        
        players_detected = check_for_players(radius=11, max_wait_ticks=2)
        
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
    walk_to_turoth()
    hop_if_players_nearby()


if __name__ == "__main__":
    run()

