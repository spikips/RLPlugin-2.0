# modules/utils/potions.py - Shared potion utilities (eliminates duplication)
from modules.utils.inventory import check_inventory

def get_total_doses(potion_base: str) -> int:
    """Total doses across all variants (1-4). Used by nmz_main, withdraw_potions, etc."""
    total = 0
    for dose in range(1, 5):
        name = f"{potion_base} ({dose})"
        exists, count, _ = check_inventory(name)
        total += count * dose
    return total

def has_potion_type(potion_base: str) -> bool:
    """Quick check if any dose exists."""
    return any(check_inventory(f"{potion_base} ({d})")[0] for d in range(1, 5))