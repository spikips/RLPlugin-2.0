import time
import random
import keyboard

from modules.core.plugin_client import npc, inventory, stats as plugin_stats
from modules.core.mouse_control import move as mouse
from modules.core.window_utils import runelite_window
from modules.utils.banking import bank
from modules.utils.logout import logout_and_break

def crafting(allow_break=True):
    """
    Automate crafting sapphires: withdraw chisel and uncut sapphires, craft them, deposit products,
    and repeat until no uncut sapphires remain in the bank.

    - Checks if bank is open; if not, opens it via Banker NPC (ID: 1634).
    - Withdraws 1 chisel and 27 uncut sapphires; exits if either has quantity 0.
    - Crafts sapphires until none remain in inventory.
    - Repeats the process.
    """
    rl_x, rl_y = runelite_window(0, 0)
    crafting_level = plugin_stats().get('data', {}).get('Crafting', {}).get('level', 0)
    print(f"Debug: Initial Crafting level: {crafting_level}")
    while True:
        # Check if bank is open
        if not bank(deposit_inventory=True):
            print("Bank interface not open, finding Banker NPC")
            banker_data = npc(id="1634", name="Banker", middle_point=True)
            if not banker_data or 'data' not in banker_data or not banker_data['data']:
                print("No Banker NPC (ID: 1634) found, exiting")
                exit()
            banker = banker_data['data'][0]
            middle_point = banker.get('middle_point')
            if middle_point:
                x, y = middle_point['x'], middle_point['y']
                mouse(x + rl_x, y + rl_y, button="left", fast=True, sleep=True)
                print(f"Clicked Banker at x={x + rl_x}, y={y + rl_y}")
                for a in range(12):
                    if bank(withdraw="chisel", deposit_inventory=True, placeholder=True, amount="1", unnoted=True):
                        if not bank(withdraw="uncut sapphire", placeholder=True, amount="all", unnoted=True):
                            print("Failed to withdraw uncut sapphires, likely quantity 0, exiting")
                            exit()
                        break
                    elif a == 11:
                        exit('failed to open bank')
                    time.sleep(0.1)
            else:
                print("No middle_point for Banker, exiting")
                exit()

        # Open inventory
        keyboard.press_and_release("esc")
        print("Pressed Esc")
        time.sleep(random.uniform(0.32, 0.42))
        keyboard.press_and_release("f1")
        print("Pressed F1")
        time.sleep(random.uniform(0.32, 0.42))

        # Crafting loop with retry for inventory detection
        attempts = 0
        max_attempts = 3
        while attempts < max_attempts:
            # Check for uncut sapphires
            sapphire_data = inventory(item="uncut sapphire", middle_point=True)
            if not sapphire_data or 'data' not in sapphire_data or not sapphire_data['data']:
                print("No uncut sapphires in inventory, retrying detection")
                time.sleep(0.5)  # Wait for inventory to update
                attempts += 1
                if attempts == max_attempts:
                    print("No uncut sapphires found after retries, proceeding to bank")
                    break
                continue
            attempts = 0  # Reset on successful detection

            # Get chisel and sapphire coordinates
            chisel_data = inventory(item="chisel", middle_point=True)
            if not chisel_data or 'data' not in chisel_data or not chisel_data['data']:
                print("No chisel in inventory, exiting")
                exit()
            chisel = chisel_data['data'][0]
            chisel_middle = chisel.get('middle_point')
            if not chisel_middle:
                print("No middle_point for chisel, exiting")
                exit()

            sapphire = sapphire_data['data'][0]
            sapphire_middle = sapphire.get('middle_point')
            if not sapphire_middle:
                print("No middle_point for uncut sapphire, exiting")
                exit()

            while True:
                # Click chisel then sapphire
                x, y = chisel_middle['x'], chisel_middle['y']
                mouse(x + rl_x, y + rl_y, button="left", fast=True, sleep=True)
                print(f"Clicked chisel at x={x + rl_x}, y={y + rl_y}")
                time.sleep(random.uniform(0.05, 0.1))
                x, y = sapphire_middle['x'], sapphire_middle['y']
                mouse(x + rl_x, y + rl_y, button="left", fast=True, sleep=True)
                print(f"Clicked uncut sapphire at x={x + rl_x}, y={y + rl_y}")
                time.sleep(random.uniform(0.05, 0.1))

                # Space press loop
                for i in range(10):
                    if i == 9 or random.random() < 0.5:  # 100% on last, 50% otherwise
                        keyboard.press_and_release("space")
                        print("Pressed Space")
                    time.sleep(0.1)

                while True:
                    # Recheck sapphires to continue or break
                    sapphire_data = inventory(item="uncut sapphire", middle_point=True)
                    if not sapphire_data or 'data' not in sapphire_data or not sapphire_data['data']:
                        print("No uncut sapphires remaining, proceeding to bank")
                        break
                    time.sleep(1)

                # Check for level up after crafting batch
                new_crafting_level = plugin_stats().get('data', {}).get('Crafting', {}).get('level', 0)
                if new_crafting_level != crafting_level:
                    crafting_level = new_crafting_level
                    print(f"Debug: Updated Crafting level to {crafting_level}")

                if allow_break:
                    # Add sleep timers after every inventory
                    if random.random() < 0.15:
                        sleep_time = random.uniform(15, 180)
                        print(f"Debug: Short AFK sleep for {sleep_time:.1f} seconds")
                        time.sleep(sleep_time)
                    if random.random() < 0.01:
                        break_time = random.uniform(30 * 60, 90 * 60)  # 30-90 minutes in seconds
                        print(f"Debug: Long break for {break_time / 60:.1f} minutes")
                        logout_and_break(break_time)

                # Find Banker to reopen bank
                banker_data = npc(id="1634", name="Banker", middle_point=True)
                if not banker_data or 'data' not in banker_data or not banker_data['data']:
                    print("No Banker NPC (ID: 1634) found, exiting")
                    exit()
                banker = banker_data['data'][0]
                middle_point = banker.get('middle_point')
                if middle_point:
                    x, y = middle_point['x'], middle_point['y']
                    mouse(x + rl_x, y + rl_y, button="left", fast=True, sleep=True)
                    print(f"Clicked Banker at x={x + rl_x}, y={y + rl_y}")
                    time.sleep(1)
                else:
                    print("No middle_point for Banker, exiting")
                    exit()

                # Deposit sapphires and withdraw more
                sapphire_deposited = None
                for _ in range(10):
                    sapphire_deposited = bank(deposit="sapphire", placeholder=True, amount="all", unnoted=True)
                    if sapphire_deposited:
                        print("Successfully deposited sapphires")
                        break
                    print("Failed to deposit sapphires, retrying")
                    time.sleep(0.1)
                if sapphire_deposited:
                    if not bank(withdraw="uncut sapphire", placeholder=True, amount="all", unnoted=True):
                        print("Failed to withdraw uncut sapphires, likely quantity 0, exiting")
                        exit()
                else:
                    print("Failed to deposit sapphires after 10 attempts, exiting")
                    exit()

                # Close bank and restart
                keyboard.press_and_release("esc")
                print("Pressed Esc")
                time.sleep(random.uniform(0.62, 0.75))

crafting(allow_break=False)