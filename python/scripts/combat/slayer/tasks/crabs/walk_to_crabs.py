import keyboard

from modules.npc_data.click_npc import click_closest_npc
from modules.object_data.game_object import click_gameobject
from modules.player_data.ensure_correct_attack_style import ensure_correct_combat_style
from modules.player_data.tile_change import wait_for_tile_change, wait_until_at_tile
from modules.player_data.wait_till_character_stops_moving import wait_till_character_stopped_moving
from modules.utils.camera import camera
from modules.utils.click_minimap_tile import click_minimap_tile
from modules.utils.click_tile import click_tile
from modules.utils.automatic_scripting.small_functions import click_equipped_glory
from modules.utils.loot import wait_for_next_tick
from modules.utils.wait_for_tick import wait_for_tick
from modules.widgets.widget import check_widget, check_widget_text, click_widget_child

from modules.utils.hop import hop_to_random_world
from modules.banking.bank_castlewars import bank_castlewars
from modules.utils.check_players import check_for_players
from scripts.combat.slayer.slayer_gear import get_target_gear
from scripts.combat.slayer.utils.slayer_task_utils import check_if_need_for_hop, hop_until_empty, hop_until_empty


def go_to_bank():
    """Go to bank and get target gear and inventory."""
    target_gear = get_target_gear()

    target_inventory = {
    "Prayer potion": 6,
    "Games necklace": 1,
    "Amulet of glory": 1,
    "Ring of dueling": 2,
}

    bank_castlewars(target_gear=target_gear, target_inventory=target_inventory)
    ensure_correct_combat_style()

def walk_to_crabs():
    """Walk to the crabs location."""
    for i in range(5):
        if click_equipped_glory(action='Draynor Village'):
            wait_for_tile_change()
            wait_for_next_tick()
            break
        wait_for_next_tick()
        if i == 4:
            exit("Failed to click jewelry: Amulet of glory(3) (Draynor Village)")

    # 2
    for i in range(5):
        if click_widget_child('35913752', sprite_id=None, hidden=False, child_index=1, right_click=False, action=None):
            break
        wait_for_next_tick()
        if i == 4:
            exit("Failed to click dialogue option (look north) via child")

    # 3
    for i in range(3):
        if camera(pitch=341, yaw=0, zoom=380, speed=10):
            break
        if i == 2:
            exit("Failed to set camera")

    # 4
    for i in range(10):
        if click_minimap_tile(3071, 3259, rand_x=1, rand_y=1, target_zoom=2.0):
            print("clicked minimap tile (3071, 3259)")
            if wait_till_character_stopped_moving():
                break
        wait_for_next_tick()
        if i == 9:
            exit("Failed to click minimap tile (3073, 3259)")


    # 6
    for i in range(10):
        if click_minimap_tile(3057, 3245, rand_x=1, rand_y=1, target_zoom=2.0):
            print("clicked minimap tile (3057, 3245)")
            for i in range(3):
                if camera(pitch=335, yaw=1196, zoom=352, speed=10):
                    break
                if i == 2:
                    exit("Failed to set camera")
            if wait_till_character_stopped_moving():
                wait_for_next_tick(3)
                break
        wait_for_next_tick()
        if i == 9:
            exit("Failed to click minimap tile (3054, 3245)")

    # 8
    first_time = False
    for i in range(10):
        if not click_closest_npc([8630], option='Port piscarilius', max_attempts=5):
            wait_for_next_tick()
            if click_closest_npc([8484], option='talk-to', max_attempts=5):
                for i in range(5):
                    if check_widget('10617398'):    
                        print('found click here to continue text')
                        while check_widget('10617398'):
                            if check_widget_text('14352385', child_index=1) == "Where's that?":
                                print('found')
                                click_widget_child(id_str=14352385, child_index=1)
                            if check_widget_text('14352385', child_index=1) == "That's great, can you take me there please?":
                                print('found')
                                click_widget_child(id_str=14352385, child_index=1)
                            keyboard.press_and_release('space')
                            wait_for_next_tick() 
                        if wait_until_at_tile(1824, 3691, plane=0):
                            wait_for_next_tick(6)
                            first_time = True
                            break       
                    wait_for_next_tick()
        else:
            if wait_until_at_tile(1824, 3695, plane=1):
                wait_for_next_tick(6)
                break
        if first_time:
            break
        if i == 9:
            exit("Failed to click npc (veos)")
        

    # 1
    if not first_time:
        for i in range(5):
            if click_gameobject("27778", 'cross', tile=(1824, 3693), radius=20):
                wait_till_character_stopped_moving()
                wait_for_next_tick(3)
                break
            wait_for_next_tick()
            if i == 4:
                exit("Failed to click object (gangplank, cross)")

    # 2
    for i in range(10):
        if click_minimap_tile(1795, 3669, rand_x=1, rand_y=1, target_zoom=2.0):
            print("clicked minimap tile (1795, 3669)")
            for i in range(3):
                if camera(pitch=266, yaw=1161, zoom=253, speed=10):
                    break
                if i == 2:
                    exit("Failed to set camera")
            if wait_till_character_stopped_moving():
                break
        wait_for_next_tick()
        if i == 9:
            exit("Failed to click minimap tile (1795, 3669)")



    # 1
    for i in range(10):
        if click_minimap_tile(1795, 3646, rand_x=2, rand_y=2, target_zoom=2.0):
            print("clicked minimap tile (1795, 3646)")
            if wait_till_character_stopped_moving():
                break
        wait_for_next_tick()
        if i == 9:
            exit("Failed to click minimap tile (1795, 3646)")

    # 2
    for i in range(10):
        if click_minimap_tile(1804, 3624, rand_x=2, rand_y=2, target_zoom=2.0):
            print("clicked minimap tile (1804, 3624)")
            if wait_till_character_stopped_moving():
                break
        wait_for_next_tick()
        if i == 9:
            exit("Failed to click minimap tile (1804, 3624)")

    # 3
    for i in range(10):
        if click_minimap_tile(1812, 3606, rand_x=2, rand_y=2, target_zoom=2.0):
            print("clicked minimap tile (1812, 3606)")
            if wait_till_character_stopped_moving():
                break
        wait_for_next_tick()
        if i == 9:
            exit("Failed to click minimap tile (1812, 3606)")

    # 4
    for i in range(10):
        if click_minimap_tile(1816, 3587, rand_x=2, rand_y=2, target_zoom=2.0):
            print("clicked minimap tile (1816, 3587)")
            if wait_till_character_stopped_moving():
                break
        wait_for_next_tick()
        if i == 9:
            exit("Failed to click minimap tile (1816, 3587)")

    # 5
    for i in range(10):
        if click_minimap_tile(1838, 3579, rand_x=2, rand_y=2, target_zoom=2.0):
            print("clicked minimap tile (1838, 3579)")
            if wait_till_character_stopped_moving():
                break
        wait_for_next_tick()
        if i == 9:
            exit("Failed to click minimap tile (1838, 3579)")

    # 6
    for i in range(10):
        if click_minimap_tile(1851, 3563, rand_x=2, rand_y=2, target_zoom=2.0):
            print("clicked minimap tile (1851, 3563)")
            if wait_till_character_stopped_moving():
                break
        wait_for_next_tick()
        if i == 9:
            exit("Failed to click minimap tile (1851, 3563)")

    # 7
    for i in range(10):
        if click_minimap_tile(1859, 3553, rand_x=2, rand_y=2, target_zoom=2.0):
            print("clicked minimap tile (1859, 3553)")
            if wait_till_character_stopped_moving():
                break
        wait_for_next_tick()
        if i == 9:
            exit("Failed to click minimap tile (1859, 3553)")


    # 8
    for i in range(3):
        if click_tile(1865, 3553, plane=0, action="Walk here", tile_radius=2, right_click=False):
            if wait_till_character_stopped_moving():
                    break
            if i == 2:
                exit("Failed to walk to (1865, 3553)")


def hop_if_players_nearby():
    """Hop worlds if players are detected nearby."""
    hop_tile = (1836, 3561, 0)
    stand_tile = (1865, 3553, 0)

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
        if check_if_need_for_hop():
            hop_until_empty()

        players_detected = check_for_players(radius=10, max_wait_ticks=2)

        if not players_detected:
            click_minimap_tile(stand_tile[0], stand_tile[1], target_zoom=2.0)
            wait_till_character_stopped_moving(required_idle_ticks=2)
            break


def run():
    """Execute the main sequence: go to bank, walk to location, and check for players."""
    go_to_bank()
    walk_to_crabs()
    hop_if_players_nearby()


if __name__ == "__main__":
    run()
