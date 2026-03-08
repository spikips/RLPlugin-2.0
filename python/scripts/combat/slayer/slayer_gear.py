"""
items required:

holy sandals,
ancient cloak, 
Monk's robe
Monk's robe top
Amulet of glory
Combat bracelet
Honourable blessing
Ring of wealths
ring of duelings
zombie axe
antler guard
glacial temotli
brine sabre
cannon
cannonballs
prayer potions
nature runes
fire runes
games necklaces
necklace of passage(5)
salve graveyard teleport
Fenkenstrain's castle teleport
barrows teleport
camelot teleport
antidote++(4)
waterskin(4)
"""
# slayer_gear.py
# This module dynamically determines the best possible non-jewelry gear for Hill Giant slayer tasks
# based on your Attack level, what you're currently wearing, and what is available (equipped / inventory / bank).
# Jewelry is still ignored — add it separately in your main script.

from modules.core.plugin_client import stats, gear
from modules.fetch_data.fetch_bank_items import fetch_bank_items
from modules.utils.inventory import check_inventory

# Common non-jewelry, non-weapon items
BASE_GEAR = [
    "Ancient cloak",
    "holy sandals",
    "Monk's robe",
    "Monk's robe top",
    "Amulet of glory",
    "Combat bracelet",
    "Honourable blessing",
    "Ring of wealth"
]

# Tier-specific gear lists
TIER_65_GEAR = ["Zombie axe", "Antler guard"]                    # 65 Attack
TIER_55_GEAR = ["Glacial temotli"]                               # 55 Attack
TIER_40_GEAR = ["Brine sabre", "Antler guard"]                   # 40 Attack


def _item_available(item_name: str) -> bool:
    """Check if an item is equipped OR in inventory OR in bank (qty >= 1)."""
    # 1. Equipped
    equipped = set(gear()["data"].keys())
    if item_name in equipped:
        return True

    # 2. Inventory (lowercase to match existing check_inventory style used for Slayer helmet)
    in_inventory, _, _ = check_inventory(item_name.lower())
    if in_inventory:
        return True

    # 3. Bank
    return fetch_bank_items([(item_name, 1)])


def _slayer_helmet_available() -> bool:
    """Check if slayer helmet is equipped, in inventory, or in bank."""
    equipped_items = gear().get("data", {})
    if "Slayer helmet" in equipped_items:
        return True
    in_inventory, _, _ = check_inventory("slayer helmet")
    if in_inventory:
        return True
    return fetch_bank_items([("slayer helmet", 1)])


def get_target_gear() -> list[str]:
    """
    Returns the full target_gear list (base + headgear + tier-specific items).
    Now also checks inventory for every weapon/offhand.
    """
    player_stats = stats()["data"]
    attack_level = player_stats.get("Attack", {}).get("level", 1)

    target_gear = BASE_GEAR.copy()

    # Dynamic headgear
    if _slayer_helmet_available():
        target_gear.append("slayer helmet")
        print("Slayer helmet available (equipped/inventory/bank) — using as headgear")
    else:
        target_gear.append("Ancient mitre")
        print("No slayer helmet found — falling back to Ancient mitre")

    # Highest tier first
    if attack_level >= 65 and _item_available("Zombie axe"):
        target_gear += TIER_65_GEAR
        return target_gear

    if attack_level >= 55 and _item_available("Glacial temotli"):
        target_gear += TIER_55_GEAR
        return target_gear

    # Fallback tier
    if attack_level >= 40:
        if _item_available("Brine sabre") and _item_available("Antler guard"):
            target_gear += TIER_40_GEAR
            return target_gear

    print(f"Insufficient gear for Hill Giants slayer. Attack level: {attack_level}")
    print("Required: Glacial temotli (55 Att) or Brine sabre + Antler guard (40 Att)")
    exit("Missing required slayer gear — stopping script")


get_target_gear()