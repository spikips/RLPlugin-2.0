from modules.player_data.tile_change import wait_for_tile_change
from modules.player_data.wait_till_character_stops_moving import wait_till_character_stopped_moving
from modules.utils.camera import camera
from modules.utils.check_if_in_tile import click_tile
from modules.utils.click_minimap_tile import click_minimap_tile
from modules.utils.inventory import click_inventory
from modules.utils.wait_for_tick import wait_for_next_tick, wait_for_tick


from modules.utils.hop import hop_to_random_world
from modules.banking.bank_castlewars import bank_castlewars
from modules.utils.check_players import check_for_players
from scripts.combat.slayer.slayer_gear import get_target_gear

target_gear = get_target_gear()

target_inventory = {
    "Prayer potion": 6,
    "Games necklace": 1,
    "Amulet of glory": 1,
    "Ring of dueling": 2,
    "Barrows teleport": 1
}

bank_castlewars(target_gear=target_gear, target_inventory=target_inventory)


1
for i in range(5):
    if click_inventory('barrows teleport', action='break', hover_only=False):
        wait_for_tile_change()
        wait_for_next_tick(2)
        break
    wait_for_next_tick()
    if i == 4:
        exit("Failed to click inventory item (Barrows teleport, Break)")

# 3
for i in range(3):
    if camera(pitch=321, yaw=0, zoom=206, speed=10):
        break
    if i == 2:
        exit("Failed to set camera")

# 4
for i in range(10):
    if click_minimap_tile(3537, 3296, rand_x=2, rand_y=2, target_zoom=2.0):
        print("clicked minimap tile (3537, 3296)")
        if wait_till_character_stopped_moving():
            break
    wait_for_next_tick()
    if i == 9:
        exit("Failed to click minimap tile (3537, 3296)")

# 6
for i in range(10):
    if click_minimap_tile(3522, 3279, rand_x=2, rand_y=2, target_zoom=2.0):
        print("clicked minimap tile (3522, 3279)")
        if wait_till_character_stopped_moving():
            break
    wait_for_next_tick()
    if i == 9:
        exit("Failed to click minimap tile (3522, 3279)")

# 7
for i in range(10):
    if click_minimap_tile(3509, 3303, rand_x=2, rand_y=2, target_zoom=2.0):
        print("clicked minimap tile (3509, 3303)")
        if wait_till_character_stopped_moving():
            break
    wait_for_next_tick()
    if i == 9:
        exit("Failed to click minimap tile (3509, 3303)")

# 8
for i in range(3):
    if click_tile(3506, 3312, action="Walk here", tile_radius=2, right_click=False):
       if wait_till_character_stopped_moving():
            break
    if i == 2:
        exit("Failed to walk to (3506, 3312)")


hop_tile =  (3506, 3317, 0)
stand_tile =  (3506, 3312, 0)

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
    if not hop_to_random_world('p2p'):
        print("Hop failed -> retrying check")
        wait_for_tick(3)
        continue

    click_minimap_tile(stand_tile[0], stand_tile[1], target_zoom=2.0)


else:
    exit('Too many hops')

from scripts.combat.slayer.shades import main

main()