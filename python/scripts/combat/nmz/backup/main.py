from check_area_start_and_open_bank import open_bank
from check_gear import check_gear
from nmz_bank import nmz_bank
from modules.utils.banking import bank
from modules.utils.click_minimap_tile import click_minimap_tile
from modules.utils.camera import camera
from nmz_dream import enter_dream
from check_nmz_chat_options import check_nmz_chat_options
from modules.player_data.tile_change import wait_for_tile_change
from modules.utils.wait_for_tick import wait_for_tick
from modules.object_data.game_object import click_gameobject
from vial_ui import boss_config
from modules.widgets.widget import check_widget
from modules.utils.logout import logout_and_break 
from monitor_nmz_plane import monitor_nmz_plane
from modules.core.window_utils import focus_runelite_window
import random
import datetime

def sleeptimer():
    # Generate random sleep time in minutes (between 20 and 80)
    sleep_minutes = random.randint(20, 80)

    # Get current time
    current_time = datetime.datetime.now()

    # Calculate end time
    end_time = current_time + datetime.timedelta(minutes=sleep_minutes)

    # Print current time and end time
    print(f"Current time: {current_time.strftime('%H:%M:%S')}")
    print(f"Sleep duration: {sleep_minutes} minutes")
    print(f"Timer will complete at: {end_time.strftime('%H:%M:%S')}")
    return sleep_minutes

def main():
    """Main script to check area, verify gear, and withdraw/equip missing gear if needed, then enter NMZ."""
    print("Starting NMZ gear check and banking process...")
    
    # Step 1: Check if in NMZ outside area and open bank
    if open_bank():
        print("Bank successfully opened, proceeding to check gear.")
        
        # Step 2: Check equipped gear
        gear_message, missing_items, inventory_items = check_gear()
        print(gear_message)
        
        # Step 3: If gear is missing, withdraw and equip it
        if missing_items:
            print("Proceeding to withdraw and equip missing gear...")
            success = nmz_bank()
            if success:
                print("All missing gear items successfully withdrawn and equipped.")
                # Recheck gear to confirm all items are equipped
                gear_message, missing_items, inventory_items = check_gear()
                print(gear_message)
                if missing_items:
                    print("Some gear items still missing after withdrawal attempt. Aborting.")
                    return False
            else:
                print("Failed to withdraw or equip some gear items.")
                return False
        else:
            prayer_pot = bank(withdraw="prayer potion(4)", quantity="all", deposit_inventory=True)
            print("prayer pot", prayer_pot)
            print("No gear withdrawal needed.")
        
        # Step 4: Move to Dominic Onion and adjust camera
        click_minimap_tile(2608, 3114, 2, 2, target_zoom=2)
        wait_for_tick(2)
        # Wait until character stops moving (no tile change for 2 ticks)
        print("Waiting for character to stop moving...")
        while wait_for_tile_change(timeout_ticks=2):
            pass  # Loop until no tile change in 2 ticks
        print("Character has stopped moving.")
        
        camera(pitch=356, yaw=230, zoom=272)
        
        # Step 5: Interact with NPC and enter dream
        if enter_dream():
            # Wait 2 additional ticks
            wait_for_tick(2)
            
            # Handle chat options
            if check_nmz_chat_options():
                # Click on the game object
                click_gameobject('26291', 'Drink', (2605, 3117), 5)
                
                # Loop for max 20 ticks to check for widget '8454146'
                max_ticks = 20
                tick_count = 0
                while tick_count < max_ticks:
                    if check_widget('8454146'):
                        print(f"Vial UI widget '8454146' appeared after {tick_count} ticks.")
                        # Run vial_ui.py boss_config
                        if boss_config():
                            print("Boss configuration completed successfully.")
                        else:
                            print("Failed to configure bosses.")
                        break
                    wait_for_tick(1)
                    tick_count += 1
                if tick_count >= max_ticks:
                    print("Vial UI widget '8454146' did not appear after 20 ticks.")
                
                print("Successfully entered NMZ dream.")
                wait_for_tile_change()

                monitor_nmz_plane()
                focus_runelite_window()
                
                logout_and_break(sleeptimer())
                return True
            else:
                print("Failed to handle NMZ chat options.")
        else:
            print("Failed to enter NMZ dream after maximum attempts.")
    else:
        print("Failed to open bank, aborting process.")
    return False

if __name__ == "__main__":
    while True:
        if not main():
            exit('main failed')