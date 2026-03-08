from modules.player_data.wait_till_character_stops_moving import wait_till_character_stopped_moving
from modules.utils.automatic_scripting.small_functions import click_lowest_ring_of_dueling
from modules.utils.camera import camera
from modules.utils.check_if_in_tile import click_tile
from modules.utils.click_minimap_tile import click_minimap_tile
from modules.utils.wait_for_tick import wait_for_next_tick, wait_for_tick


from modules.utils.hop import hop_to_random_world
from modules.banking.bank_castlewars import bank_castlewars
from modules.utils.check_players import check_for_players
from scripts.combat.slayer.slayer_gear import get_target_gear
from scripts.combat.slayer.tasks.ankou.walk_to_ankou import go_to_bank

def go_to_bank():
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


def walk_to_ogres():
    # teleport to castlewars
    # for i in range(5):
    #     if click_lowest_ring_of_dueling(action='Rub'):
    #         break
    #     wait_for_next_tick()
    #     if i == 4:
    #         exit("Failed to click jewelry: Ring of dueling(7) (Rub)")

    # # 2
    # for i in range(5):
    #     if click_widget_child('14352385', sprite_id=None, hidden=False, child_index=2, right_click=False, action=None):
    #         wait_for_tile_change()
    #         wait_for_next_tick(2)
    #         break
    #     wait_for_next_tick()
    #     if i == 4:
    #         exit("Failed to click dialogue option (castle wars arena.) via child")

    # 5
    for i in range(10):
        if click_minimap_tile(2468, 3072, rand_x=2, rand_y=2, target_zoom=2.0):
            print("clicked minimap tile (2468, 3072)")
            if wait_till_character_stopped_moving():
                break
        wait_for_next_tick()
        if i == 9:
            exit("Failed to click minimap tile (2468, 3072)")

    # 6
    for i in range(10):
        if click_minimap_tile(2488, 3086, rand_x=2, rand_y=2, target_zoom=2.0):
            print("clicked minimap tile (2488, 3086)")
            if wait_till_character_stopped_moving():
                break
        wait_for_next_tick()
        if i == 9:
            exit("Failed to click minimap tile (2488, 3086)")

    # 8
    for i in range(10):
        if click_minimap_tile(2492, 3096, rand_x=2, rand_y=2, target_zoom=2.0):
            print("clicked minimap tile (2492, 3096)")
            if wait_till_character_stopped_moving():
                wait_for_tick(2)
                break
        wait_for_next_tick()
        if i == 9:
            exit("Failed to click minimap tile (2492, 3096)")

    # 9
    for i in range(3):
        if camera(pitch=330, yaw=0, zoom=573, speed=10):
            break
        if i == 2:
            exit("Failed to set camera")

    # 11
    for i in range(3):
        if click_tile(2494, 3098, action="Walk here", tile_radius=20, right_click=False):
            if wait_till_character_stopped_moving():
                    break
            if i == 2:
                exit("Failed to walk to (2494, 3098)")


def hop_if_players_nearby():
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
            wait_till_character_stopped_moving(required_idle_ticks=2)
            break

def run():
    go_to_bank()
    walk_to_ogres()
    hop_if_players_nearby()
    print("Navigation complete - ready for fighting.")

if __name__ == "__main__":
    run()