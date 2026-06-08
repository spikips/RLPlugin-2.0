from modules.core.plugin_client import gear, stats, inventory
import json
import os


def get_required_gear(attack_level, defence_level, style, prayer_fallback=False):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(script_dir, 'config.json')
    try:
        with open(json_path, 'r') as f:
            config = json.load(f)
            gear_data = config.get('gear', {}).get(style, {})
    except Exception:
        return None

    if style == 'melee':
        full_gear = []

        if prayer_fallback:
            # === PRAYER FALLBACK MODE → Force Monk's prayer gear ===
            prayer_armour = ["holy sandals", "Monk's robe", "Monk's robe top"]
            full_gear.extend(prayer_armour)
            print("Prayer Fallback Mode → forcing Monk's robe prayer bonus gear")
        else:
            # Normal defence-based armour
            defence_ranges = gear_data.get('defence_based', {})
            for level_range, items in defence_ranges.items():
                try:
                    min_l, max_l = map(int, level_range.split('-'))
                    if min_l <= defence_level <= max_l:
                        full_gear.extend(items)
                        break
                except ValueError:
                    continue

        # Common items (always included)
        full_gear.extend(gear_data.get('common', []))

        # Weapon based on Attack level (unchanged)
        weapon_ranges = gear_data.get('weapons', {})
        for level_range, items in weapon_ranges.items():
            try:
                min_l, max_l = map(int, level_range.split('-'))
                if min_l <= attack_level <= max_l:
                    full_gear.extend(items)
                    break
            except ValueError:
                continue

        return full_gear

    else:
        # Range / Magic unchanged
        for level_range, gear_list in gear_data.items():
            try:
                min_level, max_level = map(int, level_range.split('-'))
                if min_level <= attack_level <= max_level:
                    return gear_list
            except ValueError:
                continue
    return None


def check_gear(prayer_fallback=False):
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
        attack_level = player_stats.get('Attack', {}).get('level', 0)
        defence_level = player_stats.get('Defence', {}).get('level', 0)
        level_type = f"Attack {attack_level} / Defence {defence_level} (Prayer Fallback: {prayer_fallback})"
        required_gear = get_required_gear(attack_level, defence_level, style, prayer_fallback=prayer_fallback)
    elif style == 'range':
        level = player_stats.get('Ranged', {}).get('level', 0)
        level_type = 'Ranged'
        required_gear = get_required_gear(level, None, style)
    elif style == 'magic':
        level = player_stats.get('Magic', {}).get('level', 0)
        level_type = 'Magic'
        required_gear = get_required_gear(level, None, style)
    else:
        return f"Invalid style: {style}.", [], {}

    if not required_gear:
        return f"No gear requirements defined for {level_type}.", [], {}

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
        return f"All required gear items for {level_type} are equipped.", [], inventory_items
    else:
        return f"Missing gear items for {level_type}: {', '.join(missing_items)}", missing_items, inventory_items
    

if __name__ == "__main__":
    message, missing, inv_items = check_gear()
    print(message)
    if missing:
        print(f"Missing items: {missing}")