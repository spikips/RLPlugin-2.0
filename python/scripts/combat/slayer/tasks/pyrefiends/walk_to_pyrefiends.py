import time
from modules.object_data.game_object import click_gameobject
from modules.player_data.ensure_correct_attack_style import ensure_correct_combat_style
from modules.player_data.tile_change import wait_for_tile_change
from modules.player_data.wait_till_character_stops_moving import wait_till_character_stopped_moving
from modules.utils.automatic_scripting.small_functions import click_equipped_glory
from modules.utils.camera import camera
from modules.utils.click_minimap_tile import click_minimap_tile
from modules.utils.wait_for_tick import wait_for_next_tick, wait_for_tick
from modules.widgets.widget import click_widget, click_widget_child


from modules.utils.hop import hop_to_random_world
from modules.banking.bank_castlewars import bank_castlewars
from modules.utils.check_players import check_for_players
from scripts.combat.slayer.slayer_gear import get_target_gear


def go_to_bank():
    """Go to bank and get target gear and inventory."""
    target_gear = get_target_gear()

    target_inventory = {
    "Prayer potion": 5,
    "Games necklace": 1,
    "Amulet of glory": 1,
    "Ring of dueling": 2,
    "Cannon barrels": 1,
    "Cannon furnace": 1,
    "Cannon base": 1,
    "Cannon stand": 1,
    "Steel cannonball": "all",
    }

    bank_castlewars(target_gear=target_gear, target_inventory=target_inventory)
    ensure_correct_combat_style()

def walk_to_pyrefiends():
    """Walk to the pyrefiends location."""
    for i in range(5):
        if click_equipped_glory(action='Edgeville'):
            wait_for_tile_change()
            wait_for_next_tick()
            break
        wait_for_next_tick()
        if i == 4:
            exit("Failed to click jewelry: Amulet of glory(1) (Edgeville)")

    # 3
    if not click_widget('35913795', sprite_id=1030, hidden=False, right_click=False, action=None, rand_x=0, rand_y=0, clicks=1, sleep_interval=(0, 0)):
        exit(f'click widget 35913795 failed, exiting... time: {time.strftime("%H:%M:%S")}')

    # 4
    for i in range(5):
        if click_widget_child('35913752', sprite_id=None, hidden=False, child_index=1, right_click=False, action=None):
            break
        wait_for_next_tick()
        if i == 4:
            exit("Failed to click dialogue option (look north) via child")

    # 6
    for i in range(10):
        if click_minimap_tile(3082, 3474, rand_x=1, rand_y=1, target_zoom=2.0):
            print("clicked minimap tile (3082, 3474)")
            if wait_till_character_stopped_moving():
                wait_for_next_tick(2)
                break
        wait_for_next_tick()
        if i == 9:
            exit("Failed to click minimap tile (3082, 3474)")


    # 1
    # Object click: soul wars portal -> Enter
    for i in range(5):
        if click_gameobject("40474", 'Enter', tile=(3083, 3474), radius=20):
            if wait_till_character_stopped_moving():
                wait_for_tile_change()
                wait_for_next_tick(3)
                break
        wait_for_next_tick()
        if i == 4:
            exit("Failed to click object (soul wars portal, Enter)")

    # 2
    for i in range(10):
        if click_minimap_tile(2210, 2825, rand_x=2, rand_y=2, target_zoom=2.0):
            print("clicked minimap tile (2210, 2825)")
            if wait_till_character_stopped_moving():
                break
        wait_for_next_tick()
        if i == 9:
            exit("Failed to click minimap tile (2210, 2825)")

    # 3
    for i in range(10):
        if click_minimap_tile(2227, 2811, rand_x=2, rand_y=2, target_zoom=2.0):
            print("clicked minimap tile (2227, 2811)")
            if wait_till_character_stopped_moving():
                break
        wait_for_next_tick()
        if i == 9:
            exit("Failed to click minimap tile (2227, 2811)")

    # 4
    for i in range(10):
        if click_minimap_tile(2245, 2831, rand_x=2, rand_y=2, target_zoom=2.0):
            print("clicked minimap tile (2245, 2831)")
            if wait_till_character_stopped_moving():
                break
        wait_for_next_tick()
        if i == 9:
            exit("Failed to click minimap tile (2245, 2831)")

    # 5
    for i in range(10):
        if click_minimap_tile(2255, 2859, rand_x=2, rand_y=2, target_zoom=2.0):
            print("clicked minimap tile (2255, 2859)")
            if wait_till_character_stopped_moving():
                break
        wait_for_next_tick()
        if i == 9:
            exit("Failed to click minimap tile (2255, 2859)")

    # 6
    for i in range(10):
        if click_minimap_tile(2277, 2866, rand_x=2, rand_y=2, target_zoom=2.0):
            print("clicked minimap tile (2277, 2866)")
            if wait_till_character_stopped_moving():
                break
        wait_for_next_tick()
        if i == 9:
            exit("Failed to click minimap tile (2277, 2866)")

    # 7
    for i in range(3):
        if camera(pitch=324, yaw=0, zoom=207, speed=10):
            break
        if i == 2:
            exit("Failed to set camera")

    # 8
    for i in range(10):
        if click_minimap_tile(2298, 2873, rand_x=2, rand_y=2, target_zoom=2.0):
            print("clicked minimap tile (2298, 2873)")
            if wait_till_character_stopped_moving():
                break
        wait_for_next_tick()
        if i == 9:
            exit("Failed to click minimap tile (2298, 2873)")

    # 9
    for i in range(10):
        if click_minimap_tile(2319, 2887, rand_x=2, rand_y=2, target_zoom=2.0):
            print("clicked minimap tile (2319, 2887)")
            if wait_till_character_stopped_moving():
                break
        wait_for_next_tick()
        if i == 9:
            exit("Failed to click minimap tile (2319, 2887)")

    # 10
    for i in range(10):
        if click_minimap_tile(2324, 2910, rand_x=2, rand_y=2, target_zoom=2.0):
            print("clicked minimap tile (2324, 2910)")
            if wait_till_character_stopped_moving():
                break
        wait_for_next_tick()
        if i == 9:
            exit("Failed to click minimap tile (2324, 2910)")

    # 11
    for i in range(10):
        if click_minimap_tile(2321, 2940, rand_x=1, rand_y=1, target_zoom=2.0):
            print("clicked minimap tile (2321, 2940)")
            if wait_till_character_stopped_moving():
                break
        wait_for_next_tick()
        if i == 9:
            exit("Failed to click minimap tile (2321, 2940)")

    # 12
    for i in range(10):
        if click_minimap_tile(2319, 2956, rand_x=1, rand_y=1, target_zoom=2.0):
            print("clicked minimap tile (2319, 2956)")
            if wait_till_character_stopped_moving():
                break
        wait_for_next_tick()
        if i == 9:
            exit("Failed to click minimap tile (2319, 2956)")

    # 13
    for i in range(10):
        if click_minimap_tile(2293, 2962, rand_x=1, rand_y=1, target_zoom=2.0):
            print("clicked minimap tile (2293, 2955)")
            if wait_till_character_stopped_moving():
                break
        wait_for_next_tick()
        if i == 9:
            exit("Failed to click minimap tile (2293, 2955)")

    # 14
    for i in range(10):
        if click_minimap_tile(2278, 2963, rand_x=1, rand_y=1, target_zoom=2.0):
            print("clicked minimap tile (2278, 2963)")
            if wait_till_character_stopped_moving():
                break
        wait_for_next_tick()
        if i == 9:
            exit("Failed to click minimap tile (2278, 2963)")

    # 15
    for i in range(10):
        if click_minimap_tile(2257, 2958, rand_x=2, rand_y=2, target_zoom=2.0):
            print("clicked minimap tile (2257, 2958)")
            if wait_till_character_stopped_moving():
                break
        wait_for_next_tick()
        if i == 9:
            exit("Failed to click minimap tile (2257, 2958)")


def hop_if_players_nearby():
    """Hop worlds if players are detected nearby."""
    # hop until empty world
    max_hop_attempts = 15  # Safety limit to avoid infinite hopping
    for hop_attempt in range(max_hop_attempts):
        print(f"Checking for nearby players (attempt {hop_attempt + 1}/{max_hop_attempts})...")
        
        players_detected = check_for_players(radius=10, max_wait_ticks=2)
        
        if not players_detected:
            print("No players detected in 10 tile radius -> safe spot")
            break

        # click_minimap_tile(hop_tile[0], hop_tile[1], target_zoom=2.0)
        # wait_till_character_stopped_moving(required_idle_ticks=2)
        # wait_for_next_tick(8)


        print("Players detected -> hopping to new P2P world")
        if hop_to_random_world('p2p'):
            print("hopped, rechecking")
            wait_for_tick(3)
            continue

        players_detected = check_for_players(radius=10, max_wait_ticks=2)

        if not players_detected:
            # click_minimap_tile(stand_tile[0], stand_tile[1], target_zoom=2.0)
            # wait_till_character_stopped_moving(required_idle_ticks=2)
            break


def run():
    """Execute the main sequence: go to bank, walk to location, and check for players."""
    go_to_bank()
    walk_to_pyrefiends()
    hop_if_players_nearby()


if __name__ == "__main__":
    run()
