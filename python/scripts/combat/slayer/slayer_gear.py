# slayer_gear.py
# This module dynamically determines the best possible non-jewelry gear for Hill Giant slayer tasks
# based on your Attack level, what you're currently wearing, and what is available in your bank.
# It prefers the highest-tier weapon available (Glacial temotli at 55+ Attack).
# If the preferred weapon is not equipped and not in bank, it falls back to the lower-tier setup.
# Jewelry (amulet, ring, bracelet, blessing, etc.) is intentionally ignored here — add it separately
# in your main script if desired.

from modules.core.plugin_client import stats, gear
from modules.fetch_data.fetch_bank_items import fetch_bank_items


# Common non-jewelry, non-weapon items used in both tiers
BASE_GEAR = [
    "Ancient cloak",
    "Ancient mitre",
    "Climbing boots",
    "Monk's robe",
    "Monk's robe top",
    "Amulet of glory",
    "Combat bracelet",
    "Honourable blessing",
    "Ring of wealth"
]

# Tier-specific gear lists (only the varying items)
TIER_55_GEAR = ["Glacial temotli"]                               # Requires 55 Attack
TIER_40_GEAR = ["Brine sabre", "Antler guard"]                   # Requires 40 Attack (Brine sabre)


def _item_available(item_name: str) -> bool:
    """Check if an item is equipped OR present in the bank (quantity >= 1)."""
    equipped = set(gear()["data"].keys())
    if item_name in equipped:
        return True
    return fetch_bank_items([(item_name, 1)])


def get_target_gear() -> list[str]:
    """
    Returns the full target_gear list (base + tier-specific items) for use with bank_castlewars().
    Logic:
    - Get current Attack level
    - If Attack >= 55 → prefer Glacial temotli if equipped or in bank
    - Otherwise → fall back to Brine sabre + Antler guard if both are available
    - If Attack < 40 or no suitable weapon found → exit with error
    """
    player_stats = stats()["data"]
    attack_level = player_stats.get("Attack", {}).get("level", 1)

    # Highest tier first: 55+ Attack with Glacial temotli
    if attack_level >= 55 and _item_available("Glacial temotli"):
        return BASE_GEAR + TIER_55_GEAR

    # Fallback / lower tier: Brine sabre + Antler guard (requires both to be available)
    if attack_level >= 40:
        if _item_available("Brine sabre") and _item_available("Antler guard"):
            return BASE_GEAR + TIER_40_GEAR
        # Optional softer fallback: just Brine sabre if Antler guard is missing
        # Uncomment the block below if you want to allow Brine sabre without Antler guard
        """
        elif _item_available("Brine sabre"):
            print("Antler guard missing — using Brine sabre without offhand")
            return BASE_GEAR + ["Brine sabre"]
        """

    # No suitable gear found
    print(f"Insufficient gear for Hill Giants slayer. Attack level: {attack_level}")
    print("Required: Glacial temotli (55 Att) or Brine sabre + Antler guard (40 Att)")
    exit("Missing required slayer gear — stopping script")

    # Return is unreachable due to exit above, but kept for type-checking
    return BASE_GEAR