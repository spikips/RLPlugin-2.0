from modules.core.plugin_client import gear, stats, inventory
import json
import os

def get_required_gear(level, style):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(script_dir, 'config.json')
    try:
        with open(json_path, 'r') as f:
            config = json.load(f)
            gear_data = config.get('gear', {}).get(style, {})
    except Exception:
        return None

    for level_range, gear_list in gear_data.items():
        try:
            min_level, max_level = map(int, level_range.split('-'))
            if min_level <= level <= max_level:
                return gear_list
        except ValueError:
            continue
    return None

def check_gear():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(script_dir, 'config.json')
    try:
        with open(json_path, 'r') as f:
            config = json.load(f)
            style = config.get('style', 'range')
    except Exception:
        return "Config not found.", [], {}

    player_stats = stats()['data']
    if style == 'melee':
        level = player_stats.get('Attack', {}).get('level', 0)
        level_type = 'Attack'
    elif style == 'range':
        level = player_stats['Ranged']['level']
        level_type = 'Ranged'
    elif style == 'magic':
        level = player_stats['Magic']['level']
        level_type = 'Magic'
    else:
        return f"Invalid style: {style}.", [], {}

    required_gear = get_required_gear(level, style)
    if not required_gear:
        return f"No gear requirements defined for {level_type} level {level}.", [], {}

    gear_data = gear()['data']
    gear_data_lower = [item.lower() for item in gear_data]

    missing_items = [item for item in required_gear if item.lower() not in gear_data_lower]

    inventory_data = inventory(middle_point=True)['data']
    inventory_items = {}
    for item in required_gear:
        for inv_item in inventory_data:
            if inv_item.get('name', '').lower() == item.lower() and 'middle_point' in inv_item:
                inventory_items[item] = (inv_item['middle_point']['x'], inv_item['middle_point']['y'])
                break

    if not missing_items:
        return f"All required gear items for {level_type} level {level} are equipped.", [], inventory_items
    else:
        return f"Missing gear items for {level_type} level {level}: {', '.join(missing_items)}", missing_items, inventory_items
    

if __name__ == "__main__":
    message, missing, inv_items = check_gear()
    print(message)
    if missing:
        print(f"Missing items: {missing}")
    if inv_items:
        print(f"Inventory items with coordinates: {inv_items}")