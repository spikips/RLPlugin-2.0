#!/usr/bin/env python3
"""
Hueycoatl full-auto script (refactored).
Phases: bodies → head_boss → tail → head_final
"""

import sys, time, threading, queue, os, keyboard

from hueycoatl_projectile import (
    find_closest_safe_walkable_tile, get_all_gfx_objects, projectile, prayer_schedule
)
from hueycoatl_toggle_prayer import toggle_prayer
from modules.banking.banking_function import banking_function
from modules.core.mouse_control import get_cursor_pos, move
from modules.core.plugin_client import gametick, inventory, npc, player, target_npc, pick, get_active_prayers, varbit, stats
from modules.utils.loot import loot_all_ground_items, has_ground_items
from modules.npc_data.click_npc import click_closest_npc
from modules.npc_data.check_npc_animation import check_npc_animation
from modules.object_data.game_object import click_gameobject, get_game_object_tile, get_game_objects
from modules.player_data.tile_change import wait_for_tile_change
from modules.player_data.wait_till_character_stops_moving import wait_till_character_stopped_moving
from modules.utils.click_minimap_tile import click_minimap_tile
from modules.utils.inventory import click_inventory
from modules.utils.wait_for_tick import wait_for_next_tick
from modules.utils.select_menu_option import select_menu_option
from modules.utils.camera import camera
from modules.utils.click_tile import click_tile
from modules.utils.banking import bank
from modules.player_data.prayer.toggle_prayer import disable_all_prayer

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# --- Priorities ---
P_DODGE, P_PRAYER, P_ATTACK, P_MOVE, P_CAM, P_PRAYER_OFF = 0, 1, 2, 3, 4, 6

# Small additional real-time delay (on top of the game tick wait) after
# clicking a safe tile during blue avoidance. Primary protection is the
# 1-tick post_tick_wait inside dodge_blue().
BLUE_DODGE_POST_DELAY = 0.05

# Exact supplies for a Hueycoatl trip (28 inv slots when geared)
HUEY_TARGET_GEAR = [
    "Berserker ring (i)",
    "Combat bracelet(6)",
    "Ancient cloak",
    "Dual macuahuitl",
    "Blood moon helm",
    "Blood moon chestplate",
    "Dragon boots",
    "Amulet of fury",
    "Honourable blessing",
    "Blood moon tassets",
]
HUEY_TARGET_INVENTORY = {
    "Divine super combat potion(4)": 1,
    "Prayer potion(4)": 5,
    "Potato with cheese": 22,
}

# --- Mouse controller (serializes actions with cooldown) ---
class MouseCtrl:
    def __init__(self):
        self.q = queue.PriorityQueue()
        self.stop = threading.Event()
        self.last = time.time()
        self.t = threading.Thread(target=self._run, daemon=True)
        self.t.start()

    def _run(self):
        while not self.stop.is_set():
            try:
                prio, fn, a, k = self.q.get(timeout=0.05)
                if time.time() - self.last < 0.08:
                    time.sleep(0.08 - (time.time() - self.last))
                with mouse_lock:
                    try: fn(*a, **k)
                    except Exception as e: print("[MOUSE]", e)
                self.last = time.time()
                self.q.task_done()
            except queue.Empty:
                pass
            except Exception as e:
                print("[MOUSE worker]", e)

    def queue(self, prio, fn, *a, **k):
        self.q.put((prio, fn, a, k))

    def shutdown(self):
        self.stop.set()

mouse_ctrl = MouseCtrl()
mouse_lock = threading.Lock()

def q_select(x, y, opt, fast=False, prio=P_DODGE):
    mouse_ctrl.queue(prio, select_menu_option, x, y, opt, fast=fast)

def q_prayer(name, on=True, prio=None):
    if prio is None: prio = P_PRAYER if on else P_PRAYER_OFF
    mouse_ctrl.queue(prio, toggle_prayer, name, activate=on)

def ensure_piety_on():
    """Check directly via plugin (no mouse, no prayer tab needed) and only queue toggle if off.
    This avoids unnecessary hovering/clicking to 'check' Piety.
    """
    if getattr(state, 'in_prep', False):
        return
    try:
        prayer_data = get_active_prayers()
        if prayer_data and 'data' in prayer_data:
            active = prayer_data['data']
            if not active.get('PIETY', False):
                print("[PRAYER] Piety is off (direct check) — queuing to turn on")
                q_prayer('PIETY', True)
            # else: already on, do nothing — no mouse movement
    except Exception as e:
        print(f"[PRAYER] Error checking Piety state directly: {e}")
        # Fallback: queue it anyway if check fails
        q_prayer('PIETY', True)

def q_tile(x, y, action="Walk here", r=13, prio=P_MOVE):
    mouse_ctrl.queue(prio, click_tile, x, y, action=action, tile_radius=r)

# --- Shared state ---
class State:
    def __init__(self):
        self.phase = "bodies"
        self.body_idx = 0
        self.prayer_delay = 5
        self.broken_side = None
        self.blue_cd = 0
        self.stop_prayer = threading.Event()
        self.stop_hp = threading.Event()
        self.trans = threading.Event()
        self.stop_tail_mon = threading.Event()
        self.tail_event = threading.Event()
        self.tail_lock = threading.Lock()
        self.in_prep = True   # blocks hp_t / prayer_t drinks+flicks+ensure_piety until after banking
        self.entered_boss = False  # prevents trans_mon false-positive at bank

state = State()

# Body data (gate-relative)
BODIES = [
    {"name": "Body 1", "off": (-4, -8), "cam": (437, 810, 300), "npc": "hueycoatl body"},
    {"name": "Body 2", "off": (2, -9),  "cam": (408, 167, 300), "npc": "hueycoatl body"},
    {"name": "Body 3", "off": (-1, -12), "cam": (470, 128, 300), "npc": "hueycoatl body"},
    {"name": "Body 4", "off": (-4, -15), "cam": (470, 477, 300), "npc": "hueycoatl body"},
    {"name": "Body 5", "off": (-8, -12), "cam": (470, 523, 300), "npc": "hueycoatl body"},
]
HEAD_E = (-13, 4); HEAD_W1 = (-19, 4); HEAD_W2 = (-21, 4)
TAIL_E = (-11, -2); TAIL_W = (-21, -2)

GATE = (0, 0)
BODY_TILES = []
TAIL_E_T = TAIL_W_T = (0, 0)

# --- Small helpers ---
def tick():
    try:
        t = gametick()
        return int(t.get('data', 0) if isinstance(t, dict) else t)
    except:
        return 0

def wait(n=1):
    wait_for_next_tick(n)

def imminent_prayer(ahead=3):
    now = tick()
    return any(i.get('activate_at') and now <= i['activate_at'] <= now + ahead
               for i in prayer_schedule.values())

def has_blue(r=8):
    return bool(get_all_gfx_objects(3001, radius=r))

def get_data(obj):
    """Normalize plugin responses that sometimes wrap in {'data': ...}"""
    if not obj: return None
    d = obj.get('data', obj) if isinstance(obj, dict) else obj
    return d if d else None


def get_max_hitpoints() -> int:
    """Return the player's base (real) Hitpoints level from stats, which is the max HP we can restore to."""
    try:
        s = get_data(stats())
        if s:
            return int(s.get('Hitpoints', {}).get('level', 99))
    except Exception as e:
        print(f"[TOPOFF] Error fetching max HP via stats: {e}")
    return 99


def get_max_prayer() -> int:
    """Return the player's base (real) Prayer level from stats, which is the max prayer points we can restore to."""
    try:
        s = get_data(stats())
        if s:
            return int(s.get('Prayer', {}).get('level', 99))
    except Exception as e:
        print(f"[TOPOFF] Error fetching max Prayer via stats: {e}")
    return 99


def dodge_blue(r=8, search_r=6, pre_wait=0, cd=6):
    """
    If blue tiles (3001) exist, try to walk to the closest safe visible tile.
    pre_wait:       game ticks to wait *before* the move click (let current action finish).
    Returns True if we queued a dodge move.
    """
    tiles = get_all_gfx_objects(3001, radius=r)
    if not tiles:
        return False
    safe = find_closest_safe_walkable_tile(tiles, search_radius=search_r)
    if not safe:
        return False
    mp = safe.get('middle_point', {})
    x, y = mp.get('x'), mp.get('y')
    if not (x and y):
        return False

    if pre_wait > 0:
        wait(pre_wait)

    q_select(x, y, "walk here", fast=True)
    wait_for_tile_change(timeout_ticks=2)
    wait(1)

    # Small additional real-time buffer (can be tuned or removed)
    if BLUE_DODGE_POST_DELAY > 0:
        time.sleep(BLUE_DODGE_POST_DELAY)

    state.blue_cd = tick() + cd
    return True


def wait_with_blue_dodge(ticks, attack_target=None, blue_r=5, watch_head_death=False):
    """
    Wait N ticks while still dodging blue tiles.
    If watch_head_death=True, poll the head death animation (11679) every tick.
    This is important during the final reposition waits when the head is very low HP.
    """
    get_game_tick = gametick().get('data', 0)
    while gametick().get('data', 0) < get_game_tick + ticks:
        did_dodge = dodge_blue(blue_r, search_r=4, pre_wait=0, cd=3)

        if watch_head_death and is_head_death_animation():
            print("[FINAL] Death animation (11679) detected during reposition wait!")
            clear_stuck_interface()
            loot_after_death()
            return True  # will cause caller to exit

        if attack_target and not did_dodge:
            if head_dead():
                print("[FINAL] Head dead during reposition wait — skipping attack")
            else:
                attack_if_ready(attack_target)
        wait(1)
    return False


def ensure_attack(name, tries=6):
    if "hueycoatl" in name.lower() and head_dead():
        print(f"[FINAL] Skipping attack on dead head ({name}) - ID 14012 detected")
        return False
    for _ in range(tries):
        if click_closest_npc(name, option="Attack", max_attempts=3):
            wait(2)
            tgt = get_data(target_npc())
            if tgt and name.lower() in str(tgt.get('name', '')).lower():
                return True
        wait(1)
    return False

def can_attack():
    try:
        tgt = get_data(target_npc())
        if tgt and 'hueycoatl' in str(tgt.get('name', '')).lower():
            return False
        p = get_data(player(animation=True))
        return p.get('animation', -1) in (-1, 0)
    except:
        return True

def attack_if_ready(name):
    if can_attack():
        ensure_attack(name)

def cam_body(i):
    camera(*BODIES[i]["cam"])

def enter():
    camera(512, 447, 250)
    for _ in range(4):
        if click_gameobject("55401", "Quick-climb", radius=20):
            wait_till_character_stopped_moving(max_ticks=20, required_idle_ticks=2)
            state.entered_boss = True
            return
        wait()


def bank_hueycoatl():
    """Bank for Hueycoatl at the buffalo bank before entering the boss area.
    Uses the smart banking_function with exact full-dose (4) targets only (via do_huey_resupply).
    Ensures no junk, no lower-dose pots, and precisely 1 divine(4) + 5 prayer(4) + 22 potato.
    """
    print("\n[PREP] Starting Hueycoatl banking at buffalo bank...")
    ok = do_huey_resupply()
    if not ok:
        return False
    print("[PREP] Hueycoatl banking complete (full doses only, correct counts, no extras).\n")
    # Note: in_prep left False here. pre_climb_prep() will re-block monitors (hp_t etc.)
    # until after quick-climb + stop + first attack + piety on.
    return True


def head_dead():
    """Check if the main head is dead using the dead NPC ID 14012."""
    try:
        dead_data = get_data(npc(id="14012", tile=True, middle_point=True, animation=True, health=True))
        if dead_data:
            print("[DEATH] Found NPC ID 14012 → Hueycoatl is dead")
            return True
        return False
    except Exception as e:
        print(f"[DEATH] Error checking ID 14012: {e}")
        return False


def clear_stuck_interface():
    """Move mouse to break any stuck hover/interface (e.g. bank/inventory open blocking clicks)."""
    try:
        cur = get_cursor_pos()
        print(f"[FAILSAFE] Clearing stuck interface — moving mouse Y-80 from {cur}")
        move(cur[0], cur[1] - 80)   # move up to clear
        time.sleep(0.15)
        # Also try a small down nudge as backup
        move(cur[0], cur[1] + 30)
        time.sleep(0.15)
    except Exception as e:
        print(f"[FAILSAFE] clear_stuck_interface error: {e}")



def is_head_death_animation() -> bool:
    """Check for the main head's death animation (11679).
    This is timing-sensitive and should be called frequently when HP is very low."""
    return check_npc_animation(11679, 'the hueycoatl', tile_radius=15)


# === Post-death looting ===
DESIRABLE_LOOT = [
    "Hueycoatl hide",
    "Tome of earth (empty)",
    "tooth half of key (moon key)",
    "Dragon hunter wand",
    "Clue scroll (hard)",
    "Huasca seed",
    "Torstol seed",
    "Ranarr seed",
    "Lantadyme seed",
    "Avantoe seed",
    "Kwuarm seed",
    "toadflax seed",
    "Dragon bones",
    "Sunfire splinters",
    "Soiled page",
    "Air orb",
    "Raw shark",
    "sunfire splinters",
    "sun-kissed bones",
    "steel cannonball",
    "adamantite ore",
    "rune dart tip",
    "limpwurt root",
    "Adamant bolts(unf)",
    "rune mace",
    "rune scimitar",
    "adamant platebody",
    "rune plateskirt",
    "death rune",
    "earth rune",
    "cosmic rune",
    "nature rune",
]


def loot_after_death(max_ticks: int = 1):
    """
    After the head dies, loot using the proper loot_all_ground_items helper.

    - Tries to pick up all items from DESIRABLE_LOOT (and can be extended).
    - Uses human-like delays from loot.py.
    - Respects a maximum number of game ticks.
    - Stops early if no desirable items remain on the ground.
    """
    print(f"\n[LOOT] Hueycoatl dead — starting looting phase (max {max_ticks} ticks)")

    # Failsafe: clear any stuck bank/inventory interface that might be blocking loot clicks
    clear_stuck_interface()

    # Deactivate all prayers after the boss is dead (no need to keep them on while looting/sliding)
    disable_all_prayer()
    print("[LOOT] All prayers deactivated post-boss death.")

    no_progress_ticks = 0

    for t in range(1, max_ticks + 1):
        picked_this_tick = 0

        for item_name in DESIRABLE_LOOT:
            try:
                picked = loot_all_ground_items(
                    item_name,
                    tile_radius=14,
                    delay_range=(0.15, 0.40)
                )
                if picked > 0:
                    print(f"[LOOT] Tick {t}: Picked up {picked}x {item_name}")
                    picked_this_tick += picked
            except Exception as e:
                print(f"[LOOT] Error looting {item_name}: {e}")

        if picked_this_tick > 0:
            no_progress_ticks = 0
        else:
            no_progress_ticks += 1

        # Early exit if nothing has been picked for several ticks
        if no_progress_ticks >= 3:
            # Double-check with has_ground_items for safety
            if not has_ground_items(DESIRABLE_LOOT, tile_radius=14):
                print("[LOOT] No more desirable items on the ground. Stopping early.")
                break
            else:
                no_progress_ticks = 0  # reset if items still exist but we couldn't pick (inv full, etc.)

        print(f"[LOOT] Tick {t}/{max_ticks} complete. Continuing...")
        wait(1)

    print("[LOOT] Looting phase finished. Sliding out and restarting script...")

    # Slide out after looting
    for i in range(5):
        if click_gameobject("55234", 'Quick-slide', radius=20):
            wait_till_character_stopped_moving(2)
            wait_for_tile_change()
            wait_for_next_tick(4)
            print("[LOOT] Successfully slid out. Restarting script from the beginning...")
            os.execv(sys.executable, [sys.executable] + sys.argv)
            break
        wait_for_next_tick()
        if i == 4:
            exit("Failed to click object (slope, Quick-slide)")

def tail_broken():
    if check_npc_animation(11723, 'hueycoatl tail', tile_radius=12): return True
    d = get_data(npc(name="hueycoatl tail (broken)"))
    return bool(d)

def get_hp():
    d = get_data(target_npc())
    return d.get('healthRatio') if d else None

def tail_active():
    d = get_data(npc(name="hueycoatl tail"))
    return bool(d)

def current_target_name():
    if state.phase == "bodies" and state.body_idx < len(BODIES):
        return BODIES[state.body_idx]["npc"]
    if state.phase == "tail": return "hueycoatl tail"
    return "the hueycoatl"

def reliable_move(x, y, r=13, tries=3):
    for i in range(tries):
        q_tile(x, y, "Walk here", r, P_DODGE)
        if wait_for_tile_change(timeout_ticks=4):
            wait_till_character_stopped_moving(required_idle_ticks=2)
            return True
        print(f"[MOVE] retry {i+1} -> ({x},{y})")
        wait(1)
    print(f"[MOVE] FAILED ({x},{y})")
    return False

# --- Threads ---
def prayer_t():
    for i in prayer_schedule.values():
        i.setdefault('previously_present', False)
        i.setdefault('activate_at', None)
        i.setdefault('deactivate_at', None)
        i.setdefault('ignore_until', 0)

    while not state.stop_prayer.is_set():
        wait()
        if getattr(state, 'in_prep', False):
            continue
        now = tick()
        for pid, info in prayer_schedule.items():
            pres = bool(projectile(pid, radius=10))
            if now < info.get('ignore_until', 0): continue
            if pres and not info.get('previously_present'):
                info['activate_at'] = now + state.prayer_delay
            if info.get('activate_at') and now >= info['activate_at']:
                q_prayer(info['name'], True)
                # Ensure Piety is on when we flick protection — but use direct check to avoid unnecessary hover
                ensure_piety_on()
                info['deactivate_at'] = now + 2
                info['activate_at'] = None
            if info.get('deactivate_at') and now >= info['deactivate_at']:
                q_prayer(info['name'], False)
                info['deactivate_at'] = None
            info['previously_present'] = pres

def drink_prayer_potion():
    """Drink lowest dose prayer potion first, similar to slayer scripts.
    No wait(1) after drink — we can (and want to) attack immediately after potting.
    """
    doses = ['Prayer potion(1)', 'Prayer potion(2)', 'Prayer potion(3)', 'Prayer potion(4)']
    for dose in doses:
        if click_inventory(dose, action='drink'):
            print(f"[PRAYER] Drank {dose}")
            return True
    return False


def can_drink_divine_super_combat():
    """Check varbit 13663: 0 means we can drink (cooldown over)."""
    try:
        v = varbit(varbit_id=13663)
        # varbit() returns the int value directly (or None)
        return v == 0 if v is not None else False
    except Exception as e:
        print(f"[DIVINE] Error checking varbit 13663: {e}")
        return False


def drink_divine_super_combat():
    """Drink divine super combat, preferring highest dose first.
    No wait(1) after drink — we can (and want to) attack immediately after potting.
    """
    doses = ['Divine super combat potion(4)', 'Divine super combat potion(3)', 'Divine super combat potion(2)', 'Divine super combat potion(1)']
    for dose in doses:
        if click_inventory(dose, action='drink'):
            print(f"[COMBAT] Drank {dose}")
            return True
    return False


# --- Pre-climb / transition helpers for topping off + prayer disable ---

def eat_food_until_full(max_attempts: int = 30, heal_amount: int = 16) -> bool:
    """Repeatedly eat Potato with cheese until HP is "full enough".

    Conservative rule: food heals ~16, so don't consume a dose if the remaining deficit
    is small (e.g. 82/83 HP — no point eating for 1 hp). We consider "full enough"
    if deficit < heal_amount.

    Uses actual player level from stats() instead of hardcoded 99.
    """
    max_hp = get_max_hitpoints()
    for attempt in range(max_attempts):
        p = get_data(player(health=True))
        hp = p.get('health', 0) if p else 0
        deficit = max_hp - hp
        if deficit <= 0 or deficit < heal_amount:
            print(f"[TOPOFF] HP close enough to full ({hp}/{max_hp}, deficit={deficit} < ~{heal_amount}) — not eating more.")
            return True
        if not click_inventory('potato with cheese', action='eat'):
            print("[TOPOFF] No more food left to eat.")
            return False
        wait(1)  # let eat land and hp update
        # Re-fetch current on next iteration; max rarely changes
    p = get_data(player(health=True))
    hp = p.get('health', 0) if p else 0
    deficit = max_hp - hp
    print(f"[TOPOFF] Max eat attempts reached (still at {hp}/{max_hp}, deficit={deficit}).")
    return False


def drink_prayer_until_full(max_attempts: int = 20, restore_amount: int = 20) -> bool:
    """Repeatedly drink prayer potions (lowest dose first) until prayer is "full enough".

    Conservative rule: a prayer potion restores ~20 points, so don't consume one if the
    remaining deficit is small (e.g. 75/77 prayer — no point wasting a dose for 2 points).
    We consider "full enough" if deficit < restore_amount.

    Uses actual player Prayer level from stats() instead of hardcoded 99.
    """
    max_pray = get_max_prayer()
    for attempt in range(max_attempts):
        p = get_data(player(prayer=True))
        pray = p.get('prayer', 0) if p else 0
        deficit = max_pray - pray
        if deficit <= 0 or deficit < restore_amount:
            print(f"[TOPOFF] Prayer close enough to full ({pray}/{max_pray}, deficit={deficit} < ~{restore_amount}) — not drinking more.")
            return True
        if not drink_prayer_potion():
            print("[TOPOFF] No more prayer potions left.")
            return False
        wait(1)  # let drink land and prayer update (multi-dose topping needs this)
        # Re-fetch current on next iteration
    p = get_data(player(prayer=True))
    pray = p.get('prayer', 0) if p else 0
    deficit = max_pray - pray
    print(f"[TOPOFF] Max prayer drink attempts reached (still at {pray}/{max_pray}, deficit={deficit}).")
    return False


def emergency_top_up_supplies() -> bool:
    """Open the buffalo bank, withdraw extra prayer pots + food for topping off, close bank.
    Used only when the trip supplies we have are insufficient to reach full HP/prayer.
    """
    print("[PREP] Insufficient supplies to fill HP/prayer — emergency top-up at buffalo bank...")
    for i in range(5):
        if click_gameobject("55199", 'Bank', radius=20):
            break
        wait_for_next_tick()
        if i == 4:
            print("[PREP] Failed to open bank for emergency top-up.")
            return False

    wait_for_next_tick(2)

    # Withdraw a generous extra amount (exact names for full-dose)
    bank(withdraw="Prayer potion(4)", quantity="8")
    wait_for_next_tick(1)
    bank(withdraw="Potato with cheese", quantity="15")
    wait_for_next_tick(2)

    # Close bank
    keyboard.press('esc')
    time.sleep(0.08)
    keyboard.release('esc')
    wait_for_next_tick(2)

    print("[PREP] Emergency top-up withdrawn and bank closed.")
    return True


def do_huey_resupply() -> bool:
    """Run the smart banking function to ensure we have exactly the trip loadout:
    gear + 1x Divine(4) + 5x Prayer(4) + 22x Potato with cheese.
    Safe to call for initial or post-top-off cleanup (excess from emergency will be deposited).
    """
    print("[PREP] Resupplying exact trip supplies (1 divine(4) + 5 prayer(4) + 22 potato)...")
    state.in_prep = True
    ok = banking_function(
        target_gear=HUEY_TARGET_GEAR,
        target_inventory=HUEY_TARGET_INVENTORY,
        bank_object_id="55199",
        bank_action="Bank",
        bank_radius=20
    )
    state.in_prep = False
    if not ok:
        print("[PREP] Resupply failed.")
        return False
    print("[PREP] Trip resupply complete.")
    return True


def pre_climb_prep() -> None:
    """Before Quick-climb: disable all prayers, eat/drink conservatively until "full enough".
    Uses ~16 HP heal and ~20 prayer restore buffers: we stop if the remaining deficit is
    smaller than a dose (avoids wasting a potato on 82/83 HP or a prayer pot on 75/77 prayer).

    If we run out of pots/food before "full enough":
      - emergency bank top-up (extra pots/food)
      - consume them to finish topping off (conservatively)
      - re-resupply back to the exact clean trip loadout (1/5/22)
    Leaves prayers off (piety will be turned on after first attack post-climb).
    """
    print("[PREP] Pre-climb: disabling prayers + topping off HP and Prayer...")
    state.in_prep = True
    disable_all_prayer()

    had_enough = True
    if not eat_food_until_full(heal_amount=16):
        had_enough = False
    if not drink_prayer_until_full(restore_amount=20):
        had_enough = False

    if not had_enough:
        if emergency_top_up_supplies():
            print("[PREP] Consuming emergency top-up supplies to finish filling...")
            eat_food_until_full(heal_amount=16)
            drink_prayer_until_full(restore_amount=20)
            do_huey_resupply()
        else:
            print("[PREP] Could not complete emergency top-up, proceeding anyway.")

    state.in_prep = True  # keep hp_t/prayer_t blocked through the climb + first attack; unblock only after piety is turned on
    print("[PREP] Pre-climb top-off complete (prayers off, stats full or as close as possible).")


def move_to_head_and_top_off() -> bool:
    """Click minimap toward head. As soon as we start moving:
    - disable piety
    - drink prayer pots + eat food conservatively to "full enough" (while running,
      using remaining supplies). We use a ~16hp / ~20prayer buffer so we don't waste
      a full dose on 1-15 leftover points.
    When arrived (stopped moving) and we attack the head: re-enable piety.
    """
    for _ in range(10):
        if click_minimap_tile(GATE[0] + HEAD_E[0], GATE[1] + HEAD_E[1], 1, 1, target_zoom=2.0):
            if wait_for_tile_change(5):
                print("[TRANS] Started moving to head — deactivating piety, filling prayer & HP while en-route...")
                disable_all_prayer()
                drink_prayer_until_full(max_attempts=12, restore_amount=20)
                eat_food_until_full(max_attempts=20, heal_amount=16)

                wait_till_character_stopped_moving(max_ticks=20, required_idle_ticks=2)
                camera(486, 653, 428, 10)
                ensure_attack("the hueycoatl")
                ensure_piety_on()
                print("[TRANS] Arrived, attacked, piety back on.")
                return True
        wait()
    print("[TRANS] Minimap click to head did not result in move (or timed out).")
    return False


def hp_t():
    last_eat = 0
    last_prayer_drink = 0
    last_divine_drink = 0
    while not state.stop_hp.is_set():
        try:
            if getattr(state, 'in_prep', False):
                wait(1)
                continue
            p = get_data(player())
            hp = p.get('health', 99)
            prayer = p.get('prayer', 99)
            now = tick()

            # Eat if low hp
            if hp < 60 and (now - last_eat) >= 4:
                if imminent_prayer() or has_blue(8):
                    wait(1); continue
                if get_data(player(animation=True))['animation'] in (-1, 0):
                    with mouse_lock:
                        if click_inventory('potato with cheese', action='eat'):
                            last_eat = now
                            wait()
                            if state.phase != "head_final":
                                ensure_attack(current_target_name())

            # Drink prayer potion if low (20-30 threshold), lowest dose first
            if prayer < 25 and (now - last_prayer_drink) >= 4:
                # No skip for imminent here, prayer restore is important
                if get_data(player(animation=True))['animation'] in (-1, 0):
                    with mouse_lock:
                        if drink_prayer_potion():
                            last_prayer_drink = now
                            # After drinking, ensure piety is on (direct check, no mouse/hover for check)
                            ensure_piety_on()
                            # Attack immediately after pot (no tick wait) — caller already held mouse_lock for the drink click
                            attack_if_ready(current_target_name())

            # Drink Divine super combat potion whenever the cooldown allows (varbit 13663 == 0)
            if can_drink_divine_super_combat() and (now - last_divine_drink) >= 4:
                if get_data(player(animation=True))['animation'] in (-1, 0):
                    with mouse_lock:
                        if drink_divine_super_combat():
                            last_divine_drink = now
                            # After drinking divine combat boost, ensure piety
                            ensure_piety_on()
                            # Attack immediately after pot (no tick wait) — caller already held mouse_lock for the drink click
                            attack_if_ready(current_target_name())

            wait(1)
        except:
            wait(1)

def trans_mon():
    while not state.trans.is_set():
        if state.phase != "bodies":
            state.trans.set(); break
        if not getattr(state, 'entered_boss', False):
            # Do not evaluate "no bodies" or transition while still at bank / before we have climbed in
            wait(1)
            continue
        wait()
        try:
            if not get_game_objects('55206', radius=20):
                print("[TRANS] No bodies left → head")
                if move_to_head_and_top_off():
                    state.phase = "head_boss"
                    state.prayer_delay = 3
                    state.trans.set()
                else:
                    # fallback
                    state.phase = "head_boss"
                    state.prayer_delay = 3
                    state.trans.set()
                    ensure_attack("the hueycoatl")
                    ensure_piety_on()
                break
        except Exception as e:
            print("[TRANS]", e); wait(2)
    print("[TRANS] stopped")

def tail_mon():
    last = 0
    while not state.stop_tail_mon.is_set():
        try:
            if state.phase == "head_final":
                now = tick()
                if now - last < 8:
                    wait(1); continue
                if check_npc_animation(11720, "hueycoatl tail (broken)", 15):
                    d = get_data(npc(name="hueycoatl tail (broken)", tile=True))
                    side = None
                    if d:
                        for e in (d if isinstance(d, list) else [d]):
                            if 'hueycoatl tail (broken)' in str(e.get('name','')).lower():
                                tx = e.get('tile', {}).get('x')
                                if tx is not None:
                                    if abs(tx - (GATE[0]-22)) <= 2: side = "west"
                                    elif abs(tx - (GATE[0]-6)) <= 2: side = "east"
                                break
                    if side in ("west", "east"):
                        with state.tail_lock:
                            state.broken_side = side
                        state.tail_event.set()
                        last = now
                        print(f"[TAIL-MON] {side.upper()} break @ {now}")
                        wait(3)
        except Exception as e:
            print("[TAIL-MON]", e)
        wait(1)

# --- Phases ---
def bodies_phase():
    print("\n=== BODIES ===")

    # Bank before entering the boss area
    if not bank_hueycoatl():
        print("[PREP] Banking failed. Exiting.")
        return

    # Before quick-climb: disable prayers, eat to full HP, drink prayer to full.
    # If we can't reach full with current supplies -> emergency bank top-up + consume + re-resupply exact trip loadout.
    # This leaves prayers off; piety will be enabled after the first attack post-climb.
    pre_climb_prep()

    # Drink divine super combat at start if cooldown allows (boost for the whole trip).
    # Done after any pre-climb top-off / possible re-resupply so we drink from the final trip supplies.
    if can_drink_divine_super_combat():
        drink_divine_super_combat()

    enter()
    attacked = ensure_attack(BODIES[0]["npc"])
    if attacked:
        # Activate piety ONLY after quick-climb + wait stopped (in enter) + after clicking NPC to attack.
        ensure_piety_on()
    state.in_prep = False  # unblock monitors now that we are in combat with piety on
    cam_body(0)

    while state.body_idx < len(BODIES):
        if state.trans.is_set() or state.phase != "bodies": break

        b = BODIES[state.body_idx]
        now = tick()

        # living body present?
        found = False
        t = get_data(target_npc())
        if t and "hueycoatl body" in str(t.get('name','')).lower(): found = True
        if not found:
            d = get_data(npc(name="hueycoatl body"))
            if d:
                for e in (d if isinstance(d, list) else [d]):
                    if e.get('healthRatio', 0) != 0: found = True; break

        if not found:
            if not get_game_objects('55206', radius=20):
                print("[BODIES] transition to head")
                state.phase = "head_boss"
                state.prayer_delay = 3
                state.trans.set()
                move_to_head_and_top_off()  # handles minimap click + on-move disable+fill + on-arrival attack + piety on
                break
            state.body_idx += 1
            if state.body_idx < len(BODIES):
                cam_body(state.body_idx)
                ensure_attack(BODIES[state.body_idx]["npc"])
            continue

        if now >= state.blue_cd and dodge_blue(15, 10, pre_wait=1, cd=8):
            # dodge_blue() now waits 1 full game tick after the safe tile click.
            # No need to queue anything extra here — normal attack_if_ready
            # at the bottom will run on later ticks.
            pass

        attack_if_ready(b["npc"])
        wait()

def to_head():
    if state.phase != "head_boss" or not state.trans.is_set():
        print("\n=== TO HEAD ===")
        state.phase = "head_boss"
        wait(8)
        for _ in range(10):
            if click_minimap_tile(GATE[0]+HEAD_E[0], GATE[1]+HEAD_E[1], 2, 2, target_zoom=2.0):
                wait(2)
                camera(486, 653, 428, 10)
                if wait_till_character_stopped_moving(): break
            wait()
        state.prayer_delay = 3
        ensure_attack("the hueycoatl")
    else:
        print("\n=== AT HEAD (monitor) ===")
        state.prayer_delay = 3
        ensure_attack("the hueycoatl")

def boss_phase():
    print("\n=== BOSS HEAD ===")
    cd = 0
    while True:
        if get_hp() is not None and get_hp() <= 60 and tail_active():
            state.phase = "tail"; break
        now = tick()
        if now >= cd and dodge_blue(10, 4, pre_wait=1, cd=8):
            # dodge_blue handles the 1-tick wait after the safe tile click.
            cd = now + 8
        attack_if_ready("the hueycoatl")
        wait()

def tail_phase():
    print("\n=== TAIL ===")
    camera(512, 3, 258)
    click_minimap_tile(TAIL_W_T[0], TAIL_W_T[1], 1, 1)
    wait_till_character_stopped_moving(2)
    ensure_attack("hueycoatl tail")

    cd = 0
    side = "west"
    cur = TAIL_W_T

    while True:
        if tail_broken():
            state.phase = "head_final"; break

        if check_npc_animation(11721, 'hueycoatl tail', 8):
            print("[TAIL] switch")
            st = tick()
            wait(1)
            if tick() <= st: wait(1)
            side = "east" if side == "west" else "west"
            cur = TAIL_W_T if side == "west" else TAIL_E_T
            reliable_move(cur[0], cur[1], 14)
            if tail_broken(): state.phase = "head_final"; break
            ensure_attack("hueycoatl tail")
            continue

        now = tick()
        if now >= cd and dodge_blue(5, 5, pre_wait=1, cd=8):
            if tail_broken(): state.phase = "head_final"; break
            # dodge_blue() already waited 1 tick after the safe tile click.
            cd = now + 8
        attack_if_ready("hueycoatl tail")
        wait()

def final_head():
    print("\n=== FINAL HEAD ===")
    state.phase = "head_final"
    he = (GATE[0]+HEAD_E[0], GATE[1]+HEAD_E[1])
    w1 = (GATE[0]+HEAD_W1[0], GATE[1]+HEAD_W1[1])
    w2 = (GATE[0]+HEAD_W2[0], GATE[1]+HEAD_W2[1])

    reliable_move(w1[0], w1[1], 13)
    ensure_attack("the hueycoatl")
    ensure_piety_on()  # make sure piety is on for final phase flicks (direct check)

    # Drink divine boost if available at start of final phase
    if can_drink_divine_super_combat():
        drink_divine_super_combat()

    cd = 0
    while True:
        if state.tail_event.is_set():
            with state.tail_lock:
                s = state.broken_side
                state.broken_side = None
            state.tail_event.clear()

            if s == "west":
                print("[FINAL] WEST break → east 5t (dodge active) → west1")
                reliable_move(he[0], he[1], 14)
                ensure_attack("the hueycoatl")
                died = wait_with_blue_dodge(3, attack_target="the hueycoatl", watch_head_death=True)
                if died:
                    return
                reliable_move(w1[0], w1[1], 13)
                ensure_attack("the hueycoatl")
                continue
            if s == "east":
                print("[FINAL] EAST break → wait 6t (dodge active) → west2")
                died = wait_with_blue_dodge(6, attack_target="the hueycoatl", watch_head_death=True)
                if died:
                    return
                reliable_move(w2[0], w2[1], 13)
                ensure_attack("the hueycoatl")
                print("[FINAL] sustained (blue dodge on)")
                continue

        now = tick()
        if now >= cd and dodge_blue(8, 6, pre_wait=0, cd=5):
            cd = now + 5

        # === Strong death guard before any attack on the head ===
        if head_dead():
            print("[FINAL] Head dead (14012 detected) — skipping attack and going to loot")
            clear_stuck_interface()
            loot_after_death()
            return

        attack_if_ready("the hueycoatl")
        wait()

        # === Reliable head death detection ===
        hp = get_hp()
        if hp is not None and hp <= 10:
            # When very low HP, poll the death animation every single tick.
            # The animation can be very short and easy to miss otherwise.
            if is_head_death_animation():
                print("[FINAL] Death animation (11679) detected on low HP!")
                clear_stuck_interface()
                loot_after_death()
                return

        if head_dead():
            print("[FINAL] head dead (healthRatio == 0)")
            clear_stuck_interface()
            loot_after_death()
            return

        # Extra safety: always check animation even if healthRatio not yet 0
        if is_head_death_animation():
            print("[FINAL] Death animation (11679) detected!")
            clear_stuck_interface()
            loot_after_death()
            return

# --- Main ---
def main():
    global GATE, BODY_TILES, TAIL_E_T, TAIL_W_T

    g = get_game_object_tile("55401", radius=20)
    GATE = g if isinstance(g, tuple) else (g['x'], g['y'])
    for b in BODIES:
        b["tile"] = (GATE[0] + b["off"][0], GATE[1] + b["off"][1])
    BODY_TILES = [b["tile"] for b in BODIES]
    TAIL_E_T = (GATE[0] + TAIL_E[0], GATE[1] + TAIL_E[1])
    TAIL_W_T = (GATE[0] + TAIL_W[0], GATE[1] + TAIL_W[1])

    state.in_prep = True
    state.entered_boss = False

    threads = [
        threading.Thread(target=prayer_t, daemon=True),
        threading.Thread(target=hp_t, daemon=True),
        threading.Thread(target=trans_mon, daemon=True),
        threading.Thread(target=tail_mon, daemon=True),
    ]
    for t in threads: t.start()

    try:
        bodies_phase()
        to_head()
        boss_phase()
        tail_phase()
        final_head()
    finally:
        print("\n=== CLEANUP ===")
        state.in_prep = False
        state.entered_boss = False
        for ev in (state.stop_prayer, state.stop_hp, state.trans, state.stop_tail_mon):
            ev.set()
        mouse_ctrl.shutdown()
        for t in threads: t.join(1.5)
        mouse_ctrl.t.join(1.0)
        print("=== DONE ===")

if __name__ == "__main__":
    main()
