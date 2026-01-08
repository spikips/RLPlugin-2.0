import time
import random
import keyboard
from modules.core.plugin_client import game_object as Object, inventory, interact_options, main_menu
from modules.core.mouse_control import move as mouse
from modules.core.window_utils import runelite_window

def mining(rocks, tile_radius=1, drop_chance=0.35):
    """
    Mine rocks by clicking random offsets from their center, starting with the initial hover point,
    checking if the rock remains at the same tile after a successful click, and optionally dropping
    mined items. Checks for logout with check_main_menu and sleeps 35–75 minutes if at LOGIN_SCREEN.

    Args:
        rocks (str): Name of the rock to mine (e.g., "iron rocks").
        tile_radius (int): Radius to search for rocks (default: 1).
        drop_chance (float): Probability (0.0 to 1.0) to drop mined items (default: 0.35 for 35%).
    """
    rl_x, rl_y = runelite_window(0, 0)
    while True:

        ore = Object(rocks, tile_radius=tile_radius, middle_point=True)
        data_list = ore.get('data', [])

        if not data_list:
            print("No rocks available.")
            if random.random() < 0.001:  # 0.1% chance for logout
                print(f"logging out")
                mouse(651 + rl_x, 485 + rl_y, button="left", fast=True, sleep=True)
                time.sleep(random.uniform(0.22, 0.25))
                mouse(651 + rl_x, 433 + rl_y, button="left", fast=True, sleep=True)
                time.sleep(10)

            elif random.random() < 0.026:  # 2.5% chance for long break
                rand = random.random()
                if rand < 0.60:  # 60% of 2.5% = 1.5% overall
                    sleep_time = random.uniform(15, 30)
                    print(f"Sleeping for {sleep_time:.2f} seconds")
                    time.sleep(sleep_time)
                elif rand < 0.80:  # 20% of 2.5% = 0.5% overall
                    sleep_time = random.uniform(30, 45)
                    print(f"Sleeping for {sleep_time:.2f} seconds")
                    time.sleep(sleep_time)
                elif rand < 0.95:  # 15% of 2.5% = 0.375% overall
                    sleep_time = random.uniform(45, 60)
                    print(f"Sleeping for {sleep_time:.2f} seconds")
                    time.sleep(sleep_time)
                else:  # 5% of 2.5% = 0.125% overall
                    sleep_time = random.uniform(60, 180)
                    print(f"Sleeping for {sleep_time:.2f} seconds")
                    time.sleep(sleep_time)
                continue

            else:
                sleep_time = random.uniform(0.3, 3.6)
                print(f"Sleeping for {sleep_time:.2f} seconds.")
                time.sleep(sleep_time)
            continue

        for item in data_list:
            middle_point = item.get('middle_point')
            if not middle_point:
                print(f"No middle point for rock {item.get('id')}, skipping.")
                continue

            # Store the rock's identifying attributes
            tile_x, tile_y = item['tile']['x'], item['tile']['y']
            print(f"Rock at tile ({tile_x}, {tile_y})")

            # Determine click count: 3% for 3, 4% for 2, 93% for 1
            rand = random.random()
            if rand < 0.03:
                click_count = 3
            elif rand < 0.07:
                click_count = 2
            else:
                click_count = 1

            # Initial hover with random offset
            xs, ys = middle_point['x'], middle_point['y']
            hover_offset_x = random.randint(-15, 15)
            hover_offset_y = random.randint(-15, 15)
            hover_x = xs + hover_offset_x
            hover_y = ys + hover_offset_y
            mouse(hover_x + rl_x, hover_y + rl_y)  # Move mouse to hover point
            time.sleep(0.05)
            options = interact_options().get('data', [])
            is_mine_left_click = options and options[0]['option'].lower() == 'mine' and rocks.lower() in options[0]['target'].lower()

            # Track if last click was successful
            last_click_success = False

            # Perform clicks
            for i in range(click_count):
                # Use hover point for first click, refresh center for others
                if i == 0:
                    click_x, click_y = hover_x, hover_y
                else:
                    ore = Object(rocks, tile_radius=tile_radius, middle_point=True)
                    for new_item in ore.get('data', []):
                        if new_item['tile']['x'] == tile_x and new_item['tile']['y'] == tile_y:
                            middle_point = new_item.get('middle_point')
                            if middle_point:
                                center_x, center_y = middle_point['x'], middle_point['y']
                                # New random offset for subsequent clicks
                                offset_x = random.randint(-15, 15)
                                offset_y = random.randint(-15, 15)
                                click_x = center_x + offset_x
                                click_y = center_y + offset_y
                                break
                    else:
                        click_x, click_y = hover_x, hover_y  # Fallback to hover point

                # Skip first click if not "Mine" unless click_count == 3
                if i == 0 and not is_mine_left_click and click_count != 3:
                    print(f"First click skipped: not 'Mine' at x={click_x + rl_x}, y={click_y + rl_y}")
                    continue

                # Perform click and track success
                if click_count == 3 or is_mine_left_click:
                    mouse(click_x + rl_x, click_y + rl_y, button='left', fast=True, sleep=True)
                    last_click_success = True
                else:
                    mouse(click_x + rl_x, click_y + rl_y, button='right', fast=True, sleep=True)
                    time.sleep(0.05)
                    # if select_menu_option(f"mine {rocks.lower()}"):
                    #     print(f"Selected 'Mine {rocks}'.")
                    #     last_click_success = True
                    # else:
                    #     print(f"Failed to select 'Mine {rocks}', skipping click.")
                    #     last_click_success = False
                    #     continue

                print(f"Click {i+1}/{click_count} at x={click_x + rl_x}, y={click_y + rl_y}")

                if i < click_count - 1:
                    time.sleep(random.uniform(0.15, 0.2))

            # Check if rock is still present only if last click was successful
            if last_click_success:
                start_time = time.time()
                timeout = random.uniform(10, 15)  # Random timeout between 10–15 seconds
                while True:
                    elapsed_time = time.time() - start_time
                    if elapsed_time > timeout:
                        print(f"Failsafe: Rock at tile ({tile_x}, {tile_y}) still present after {elapsed_time:.2f} seconds, breaking loop.")
                        break
                    ore = Object(rocks, tile_radius=tile_radius, middle_point=True)
                    data_list = ore.get('data', [])
                    rock_found = False
                    for new_item in data_list:
                        if (new_item['tile']['x'] == tile_x and 
                            new_item['tile']['y'] == tile_y and 
                            new_item['name'].lower() == rocks.lower()):
                            rock_found = True
                            middle_point = new_item.get('middle_point')
                            if middle_point:
                                x, y = middle_point['x'], middle_point['y']
                                print(f"Rock still present, random point: x={x + rl_x}, y={y + rl_y}")
                            break
                    if not rock_found:
                        print(f"Rock at tile ({tile_x}, {tile_y}) depleted, breaking loop.")
                        break
                    time.sleep(random.uniform(0.55, 2.8))
            else:
                print(f"Last click failed, skipping rock presence check for tile ({tile_x}, {tile_y}).")


            # Optionally drop mined items based on drop_chance
            if random.random() < drop_chance:
                print(f"Dropping inventory items (chance: {drop_chance*100}%).")
                drop_items = [
                    rocks.replace(" rocks", " ore"),
                    "uncut sapphire", "uncut emerald", "uncut ruby", "uncut diamond", "clue geode"
                ]
                keyboard.press("shift")
                for item_name in drop_items:
                    items = inventory(item=item_name, middle_point=True)
                    for ore_item in items.get('data', []):
                        middle = ore_item.get('middle_point')
                        if not middle:
                            keyboard.release("shift")
                            continue
                        x, y = middle['x'] + random.randint(-10, 10) + rl_x, middle['y'] + random.randint(-10, 10) + rl_y
                        print(f"Dropping {ore_item['name']} at x={x}, y={y}")
                        mouse(x, y, button='left', fast=True, sleep=True)
                        time.sleep(random.uniform(0.05, 0.1))
                keyboard.release("shift")
            else:
                print(f"Skipping item drop (chance: {drop_chance*100}%).")


mining('Iron rocks', tile_radius=3, drop_chance=0.9)
