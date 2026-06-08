import time
from modules.core.plugin_client import stats, get_attack_style_name
from modules.widgets.widget import click_widget
from modules.utils.wait_for_tick import wait_for_next_tick  # optional but nice

# Brine Sabre (Slash Sword) widget IDs
STYLE_WIDGETS = {
    "Accurate": "38862854",    # Attack style
    "Aggressive": "38862859",  # Strength style
    "Defensive": "38862866"    # Defence style - NOW USED!
}

def get_desired_style_name() -> str:
    """Returns 'Accurate', 'Aggressive' or 'Defensive' based on your exact updated training plan."""
    data = stats()['data']
    att = data.get('Attack', {}).get('level', 1)
    strg = data.get('Strength', {}).get('level', 1)
    defe = data.get('Defence', {}).get('level', 1)

    # === DEFENCE TRAINING PHASES (checked first - exactly as you requested) ===
    if (strg >= 50 and att >= 55) and defe < 40:
        return "Defensive"
    if (strg >= 60 and att >= 65) and defe < 60:
        return "Defensive"
    if (strg >= 75 and att >= 75) and defe < 70:
        return "Defensive"
    if (strg >= 85 and att >= 85) and defe < 80:
        return "Defensive"
    if (strg >= 95 and att >= 95) and defe < 90:
        return "Defensive"
    if (strg >= 99 and att >= 99) and defe < 99:
        return "Defensive"

    # === NORMAL ATTACK / STRENGTH TRAINING (only when not in a Defence phase) ===
    # Low levels
    if strg < 50 and att >= 40:
        return "Aggressive"          # switch to Strength once Attack hits 40

    # Main progression
    if att < 55:
        return "Accurate"
    if strg < 60:
        return "Aggressive"
    if att < 65:
        return "Accurate"

    # Milestone balancing (Strength first, then Attack catches up)
    for target in [75, 85, 95, 99]:
        if strg < target:
            return "Aggressive"
        if att < target:
            return "Accurate"

    return "Aggressive"  # both 99 + Defence 99 → default Strength


def ensure_correct_combat_style():
    """
    Main function you should call before every attack loop.
    Now supports Accurate / Aggressive / Defensive automatically.
    """
    current = get_attack_style_name()
    desired = get_desired_style_name()

    # Get levels for better debug output
    data = stats()['data']
    att = data.get('Attack', {}).get('level', 1)
    strg = data.get('Strength', {}).get('level', 1)
    defe = data.get('Defence', {}).get('level', 1)

    print(f"Current style: {current} | Desired: {desired} | Attack: {att} | Strength: {strg} | Defence: {defe}")

    if current == desired:
        return True

    print(f"Switching to {desired} style...")

    # 1. Click Combat tab
    click_widget('35913792', sprite_id=1026, hidden=False, right_click=False,
                 action=None, rand_x=0, rand_y=0, clicks=1, sleep_interval=(0, 0))
    time.sleep(0.4)

    # 2. Click the correct style widget
    widget_id = STYLE_WIDGETS.get(desired)
    if widget_id:
        click_widget(widget_id, hidden=False, right_click=False, clicks=1)
        time.sleep(0.3)
        wait_for_next_tick()

    # Verify
    new_style = get_attack_style_name()
    success = new_style == desired
    return success


# Quick test (remove or comment when not needed)
if __name__ == "__main__":
    ensure_correct_combat_style()