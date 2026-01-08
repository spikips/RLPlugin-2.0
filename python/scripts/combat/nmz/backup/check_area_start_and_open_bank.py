from modules.utils.check_if_in_area import check_if_in_area
from modules.player_data.tile_change import wait_for_tile_change
from modules.utils.click_minimap_tile import click_minimap_tile
from modules.utils.camera import camera
from modules.object_data.game_object import click_gameobject
from modules.widgets.widget import check_widget

nmz_outside_tiles = [
    "2600,3119,0",
    "2600,3083,0",
    "2629,3083,0",
    "2629,3119,0",
    "2611,3127,0",
    "2600,3120,0"
]

nmz_inside_tiles = [
    "2201,3812,0",
    "2201,3808,0",
    "2201,3806,0",
    "2203,3806,0",
    "2204,3807,0",
    "2205,3807,0",
    "2205,3812,0",
    "2201,3812,0",
]

inside_bank = [
    "2607,3098,0",
    "2607,3087,0",
    "2617,3087,0",
    "2617,3098,0",
    "2607,3098,0"
]

def open_bank():
    """Check if player is in NMZ outside area, move to bank if needed, and open the bank interface."""
    nmz_outside = check_if_in_area(nmz_outside_tiles, click=False)
    nmz_inside = check_if_in_area(nmz_inside_tiles, click=False)
    print(f'outside nmz: {nmz_outside}, inside nmz: {nmz_inside}')

    if not nmz_outside:
        print('Not outside NMZ, skipping bank check')
        return False

    max_attempts = 3
    attempt = 1
    while attempt <= max_attempts:
        in_bank = check_if_in_area(inside_bank, click=False)
        if in_bank:
            print(f'Inside bank area after {attempt} attempts')
            camera_success = camera(pitch=375, yaw=1889, zoom=272)
            if camera_success:
                print('Camera adjusted to pitch=375, yaw=1889, zoom=272')
            else:
                print('Failed to adjust camera')
                return False

            # Attempt to click bank game object and open bank screen
            max_bank_attempts = 3
            bank_attempt = 1
            while bank_attempt <= max_bank_attempts:
                print(f'Attempting to click bank game object (attempt {bank_attempt}/{max_bank_attempts})')
                click_success = click_gameobject('10356', 'Bank', (2614, 3094))
                if not click_success:
                    print(f'Failed to click game object 10356 on attempt {bank_attempt}')
                    bank_attempt += 1
                    continue

                # Wait up to 10 ticks for bank screen to open
                tick_count = 0
                max_ticks = 10
                while tick_count < max_ticks:
                    if check_widget('786435'):
                        print(f'Bank screen opened after {tick_count} ticks')
                        return True  # Bank screen opened successfully
                    wait_for_tile_change(timeout_ticks=1)  # Wait 1 tick
                    tick_count += 1
                else:
                    print(f'Bank screen did not open after {max_ticks} ticks')
                    bank_attempt += 1
                    continue

            print('Failed to open bank screen after maximum attempts')
            return False

        else:
            print(f'Not in bank area, attempting to move (attempt {attempt}/{max_attempts})')
            click_minimap_tile(2611, 3094, 0, 0, target_zoom=2)
            # Keep checking until character stops moving (no tile change for 2 ticks)
            print('Waiting for character to stop moving...')
            while wait_for_tile_change(timeout_ticks=2):
                print('Character is still moving, checking again...')
            print('Character has stopped moving')
            # Check if in bank area after stopping
            in_bank = check_if_in_area(inside_bank, click=False)
            if in_bank:
                print(f'Inside bank area after stopping (attempt {attempt})')
                camera_success = camera(pitch=375, yaw=1889, zoom=272)
                if camera_success:
                    print('Camera adjusted to pitch=375, yaw=1889, zoom=272')
                else:
                    print('Failed to adjust camera')
                    return False

                # Attempt to click bank game object and open bank screen
                max_bank_attempts = 3
                bank_attempt = 1
                while bank_attempt <= max_bank_attempts:
                    print(f'Attempting to click bank game object (attempt {bank_attempt}/{max_bank_attempts})')
                    click_success = click_gameobject('10356', 'Bank', (2614, 3094))
                    if not click_success:
                        print(f'Failed to click game object 10356 on attempt {bank_attempt}')
                        bank_attempt += 1
                        continue

                    # Wait up to 10 ticks for bank screen to open
                    tick_count = 0
                    max_ticks = 10
                    while tick_count < max_ticks:
                        if check_widget('786435'):
                            print(f'Bank screen opened after {tick_count} ticks')
                            return True  # Bank screen opened successfully
                        wait_for_tile_change(timeout_ticks=1)  # Wait 1 tick
                        tick_count += 1
                    else:
                        print(f'Bank screen did not open after {max_ticks} ticks')
                        bank_attempt += 1
                        continue

                print('Failed to open bank screen after maximum attempts')
                return False

            else:
                print('Not in bank area after stopping, retrying...')
            attempt += 1

    print('Failed to reach bank area after maximum attempts')
    return False
