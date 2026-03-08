# from modules.core.plugin_client import fetch_bank_items
# print(fetch_bank_items())

import json
from typing import List, Tuple, Optional, Dict

BANK_CACHE_PATH = r"C:\Users\asd\Desktop\project\python\modules\fetch_data\bank\bank_items.json"

def load_bank_items() -> Optional[List[Dict[str, any]]]:
    """
    Load bank items from JSON cache.

    Returns:
        Optional[List[Dict[str, any]]]: List of {'name': str, 'quantity': int} or None on error.
    """
    try:
        with open(BANK_CACHE_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading bank items: {e}")
        return None

def fetch_bank_items(items_to_check: List[Tuple[str, int]]) -> bool:
    """
    Check if specified items exist in bank with at least the given quantity (case-insensitive names).

    Args:
        items_to_check: List of (item_name: str, min_quantity: int) tuples.

    Returns:
        bool: True if all items are present in sufficient quantity, False otherwise.
    """
    bank_data = load_bank_items()
    if bank_data is None:
        return False

    # Aggregate quantities by name (case-insensitive)
    bank_quantities: Dict[str, int] = {}
    for item in bank_data:
        name_lower = item['name'].lower()
        bank_quantities[name_lower] = bank_quantities.get(name_lower, 0) + item['quantity']

    for name, min_qty in items_to_check:
        name_lower = name.lower()
        if bank_quantities.get(name_lower, 0) < min_qty:
            return False

    return True

# print(fetch_bank_items([("rune scimitar", 1), ("prayer potion(4)", 5)]))
# print(fetch_bank_items([("Glacial temotli", 1)]))