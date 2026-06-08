from modules.core.plugin_client import projectiles, gfx, gametick, walkable_tile, player
from modules.utils.wait_for_tick import wait_for_next_tick
from modules.utils.select_menu_option import select_menu_option
from modules.player_data.prayer.toggle_prayer import toggle_prayer
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# ====================== PROJECTILE HELPERS ======================

def projectile(proj_id: int, radius: int = 10) -> bool:
    """Returns True if a projectile with this ID exists."""
    data = projectiles(id=str(proj_id), radius=radius)
    return bool(data and data.get('data'))


# ====================== GFX HELPERS ======================

def get_all_gfx_objects(gfx_id: int, radius: int = 10) -> list:
    """Returns ALL gfx objects with this ID (perfect for multiple blue tiles)."""
    data = gfx(id=str(gfx_id), radius=radius)
    return data.get('data', []) if data else []


# ====================== BLUE TILE EVASION ======================

def find_closest_safe_walkable_tile(blue_tiles: list, search_radius: int = 20) -> dict | None:
    """
    Returns the closest walkable tile that:
      - is NOT on any blue tile (3001)
      - has middle_point inside visible canvas (4 <= x <= 515, 4 <= y <= 337)
    """
    p_data = player(location=True)
    if not p_data or 'data' not in p_data:
        return None

    player_loc = p_data['data'].get('location') or p_data['data'].get('tile', {})
    px = player_loc.get('x') or player_loc.get('worldX', 0)
    py = player_loc.get('y') or player_loc.get('worldY', 0)

    wt_data = walkable_tile(tile_radius=search_radius)
    if not wt_data or 'data' not in wt_data or not wt_data['data']:
        return None

    walkables = wt_data['data']

    blue_set = {
        (bt.get('tile', {}).get('x'), bt.get('tile', {}).get('y'))
        for bt in blue_tiles
        if bt.get('tile')
    }

    candidates = []
    for wt in walkables:
        wx = wt.get('x')
        wy = wt.get('y')
        mp = wt.get('middle_point', {})
        mx = mp.get('x', 0)
        my = mp.get('y', 0)

        if not (4 <= mx <= 515 and 4 <= my <= 337):
            continue
        if (wx, wy) in blue_set:
            continue

        dist = ((wx - px) ** 2 + (wy - py) ** 2) ** 0.5
        candidates.append((dist, wt))

    if not candidates:
        return None

    candidates.sort(key=lambda x: x[0])
    return candidates[0][1]


# Mapping: projectile ID → prayer name
PRAYER_MAP = {
    2969: 'PROTECT_FROM_MELEE',   # melee
    2975: 'PROTECT_FROM_MAGIC',   # mage
    2972: 'PROTECT_FROM_RANGE',   # range
}

# State for each projectile type (schedules activation 5 ticks after first detection)
prayer_schedule = {
    proj_id: {
        'name': prayer_name,
        'activate_at': None,   # tick number when we should turn prayer ON
        'deactivate_at': None  # tick number when we should turn prayer OFF
    }
    for proj_id, prayer_name in PRAYER_MAP.items()
}

