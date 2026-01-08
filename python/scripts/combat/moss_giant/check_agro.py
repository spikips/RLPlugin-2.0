from modules.core.plugin_client import PluginClient

# Define NPC info - add more NPCs here
npc_info = {
    'Moss Giant': {
        'attack_anims': [4658],
        'cooldown': 6
    },
    # Add more, e.g.
    # 'Hill Giant': {
    #     'attack_anims': [4651, 4652, 4653],
    #     'cooldown': 4
    # },
}

def check_agro(npc_name: str = "") -> list:
    """
    Check aggressive NPCs, optionally filtering by a specific NPC name, and print their status.
    Returns the list of aggressive NPCs (filtered if name provided).

    Args:
        npc_name (str): Optional NPC name to filter by (case-insensitive, e.g., 'Moss Giant').
                       If empty, checks all aggressive NPCs.
    """
    client = PluginClient()

    # Set NPC config on the server
    response = client.send_request('set_npc_config', {'npc_data': npc_info})
    if response:
        print("NPC config set successfully.")

    # Get aggressive NPCs
    response = client.send_request('npc_agro', {'name': npc_name} if npc_name else {})
    if response and 'data' in response:
        data = response['data']
        if npc_name:
            if data['aggressive']:
                aggressive_npcs = [data]
            else:
                aggressive_npcs = []
        else:
            aggressive_npcs = data.get('aggressiveNpcs', [])

        # Print
        print("\nAggressive NPCs:")
        for npc in aggressive_npcs:
            name = npc['name']
            npc_id = npc['id']
            location = npc['location']
            can_reach = npc['canReach']
            on_cooldown = npc['onCooldown']
            cooldown_remaining = npc['cooldownRemaining']
            status = "green" if can_reach and not on_cooldown else "red"
            print(f"- {name} (ID: {npc_id}, Tile: {location}): Status: {status}, Can Reach: {can_reach}, "
                  f"On Cooldown: {on_cooldown}, Cooldown Remaining: {cooldown_remaining} ticks")
            if can_reach and name.lower() == 'moss giant':
                print(f"  Reachable {name} ID: {npc_id}, Tile: {location}")

        return aggressive_npcs

    print("Failed to retrieve agro data.")
    return []