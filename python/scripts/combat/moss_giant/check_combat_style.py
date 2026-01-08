from modules.core.plugin_client import stats, gear
from combat_style import get_combat_styles
from modules.core.window_utils import focus_runelite_window

def check_combat_style():
    """
    Dynamically switch combat styles based on Attack, Strength, and Defence levels.
    Priorities:
    - Aim for 40 Att, 40 Str, 40 Def initially (Attack > Strength > Defence).
    - Then Attack to 50, Strength to 50.
    - Then Attack to 60, Strength to 60.
    - Then Defence to 60.
    - Then Attack to 65, Strength to 65, Attack to 70, Strength to 75, Defence to 70,
      Attack to 75, Strength to 85, Attack to 80, Defence to 80, Attack to 85,
      Strength to 90, Attack to 90, Defence to 90, Strength to 95, Attack to 95,
      Strength to 99, Attack to 99, Defence to 99.

    Returns:
        bool: True if style is set successfully, False otherwise.
    """
    # Ensure RuneLite window is focused
    if not focus_runelite_window():
        print("Failed to focus RuneLite window.")
        return False

    # Get player stats
    stats_data = stats()
    if not stats_data or 'data' not in stats_data:
        print("Failed to retrieve player stats.")
        return False

    # Extract levels
    data = stats_data['data']
    attack_level = data.get('Attack', {}).get('level', 0)
    strength_level = data.get('Strength', {}).get('level', 0)
    defence_level = data.get('Defence', {}).get('level', 0)
    print(f"Levels - Attack: {attack_level}, Strength: {strength_level}, Defence: {defence_level}")

    # Define progression as (target_level, skill) in order of priority
    progression = [
        (40, "attack"),
        (40, "strength"),
        (40, "defence"),
        (50, "attack"),
        (50, "strength"),
        (60, "attack"),
        (60, "strength"),
        (60, "defence"),
        (70, "strength"),
        (70, "attack"),
        (75, "strength"),
        (70, "defence"),
        (75, "attack"),
        (85, "strength"),
        (80, "attack"),
        (80, "defence"),
        (85, "attack"),
        (90, "strength"),
        (90, "attack"),
        (90, "defence"),
        (95, "strength"),
        (95, "attack"),
        (99, "strength"),
        (99, "attack"),
        (99, "defence")
    ]
    
    # Map skills to their current levels
    levels = {
        "attack": attack_level,
        "strength": strength_level,
        "defence": defence_level
    }
    
    # Find the first skill in progression that hasn't reached its target level
    desired_style = "defence"  # Default if all targets met
    for target_level, skill in progression:
        if levels[skill] < target_level:
            desired_style = skill
            break

    print(f"Desired combat style: {desired_style}")

    # Determine weapon type based on equipped weapon
    gear_data = gear()
    if not gear_data or 'data' not in gear_data:
        print("Failed to retrieve gear data. Defaulting to blunt weapon.")
        weapon_type = "blunt weapon"
    else:
        # Define weapon name to type mapping
        weapon_types = {
            "toktz-xil-ak": "stab weapon",
            "dragon sword": "stab weapon",
            "granite hammer": "blunt weapon",
            "brine sabre": "slash weapon"
            # Add more weapons and their types here as needed
        }

        # Check equipped gear for a matching weapon
        equipped_items = gear_data['data']
        weapon_type = "blunt weapon"  # Default
        for item_name in equipped_items.keys():
            # Case-insensitive match
            for weapon, w_type in weapon_types.items():
                if item_name.lower() == weapon.lower():
                    print(f"Detected weapon: {item_name}, Type: {w_type}")
                    weapon_type = w_type
                    break
            if weapon_type != "blunt weapon":  # Break outer loop if weapon found
                break
        else:
            print("No recognized weapon detected in equipped items. Defaulting to blunt weapon.")

    print(f"Detected weapon type: {weapon_type}")

    # Set the combat style
    result = get_combat_styles(weapon_type, desired_style)
    if not result or 'tab_open' not in result:
        print("Failed to set combat style or tab did not open.")
        return False

    print(f"Combat styles set: {result}")
    return True

check_combat_style()