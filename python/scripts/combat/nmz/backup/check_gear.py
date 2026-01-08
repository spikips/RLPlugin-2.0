from modules.core.plugin_client import gear, stats, inventory
from gear_config import GEAR_SETS

def get_required_gear(ranged_level):
    """Return the required gear list based on the player's Ranged level."""
    for (min_level, max_level), gear_list in GEAR_SETS.items():
        if min_level <= ranged_level <= max_level:
            return gear_list
    return None  # If no gear set is defined for the level

def check_gear():
    """
    Check if the player is wearing the required gear based on their Ranged level.
    Performs case-insensitive comparison for gear names.
    Returns a tuple: (message, missing_items, inventory_items).
    - message: String indicating the gear check result.
    - missing_items: List of gear items not equipped.
    - inventory_items: Dictionary mapping gear items to their inventory coordinates (x, y) if present.
    """
    # Get player's Ranged level
    player_stats = stats()['data']
    ranged_level = player_stats['Ranged']['level']
    
    # Get the required gear for the player's Ranged level
    required_gear = get_required_gear(ranged_level)
    
    if not required_gear:
        return f"No gear requirements defined for Ranged level {ranged_level}.", [], {}
    
    # Get current gear data
    gear_data = gear()['data']
    # Convert gear_data keys to lowercase for case-insensitive comparison
    gear_data_lower = [item.lower() for item in gear_data]
    
    # Check each required item (case-insensitive)
    missing_items = [item for item in required_gear if item.lower() not in gear_data_lower]
    
    # Get inventory data to find coordinates of gear items
    inventory_data = inventory(middle_point=True)['data']
    inventory_items = {}
    for item in required_gear:
        for inv_item in inventory_data:
            if inv_item.get('name', '').lower() == item.lower() and 'middle_point' in inv_item:
                inventory_items[item] = (inv_item['middle_point']['x'], inv_item['middle_point']['y'])
                break
    
    if not missing_items:
        return f"All required gear items for Ranged level {ranged_level} are equipped.", [], inventory_items
    else:
        return (
            f"Missing gear items for Ranged level {ranged_level}: {', '.join(missing_items)}",
            missing_items,
            inventory_items
        )

if __name__ == "__main__":
    message, missing, inv_items = check_gear()
    print(message)
    if missing:
        print(f"Missing items: {missing}")
    if inv_items:
        print(f"Inventory items with coordinates: {inv_items}")