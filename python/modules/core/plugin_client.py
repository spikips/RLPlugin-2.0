import socket
import json
import time
import random
from typing import Optional, Dict, Any, List

class PluginClient:
    def __init__(self, host: str = 'localhost', port: int = 6565, auth_token: str = 'jQ8IHav3zA3HuH4'):
        """
        Initialize the PluginClient for communicating with the RuneLite plugin server.

        Args:
            host (str): The server host address (default: 'localhost').
            port (int): The server port (default: 6565).
            auth_token (str): Authentication token for server requests.
        """
        self.host = host
        self.port = port
        self.auth_token = auth_token

    def send_request(self, function_name: str, params: Dict[str, Any], retries: int = 3, delay: float = 1.0) -> Optional[Dict[str, Any]]:
        """
        Send a request to the plugin server with retry mechanism.

        Args:
            function_name (str): The function to call on the server.
            params (Dict[str, Any]): Parameters for the function.
            retries (int): Number of retry attempts for failed connections.
            delay (float): Delay in seconds between retries.

        Returns:
            Optional[Dict[str, Any]]: The parsed response data or None if all retries fail.
        """
        request_data = {
            'function': function_name,
            'params': params
        }
        request_json = json.dumps(request_data)
        message = f"{self.auth_token} {request_json}\n"

        for attempt in range(retries):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(5.0)
                    s.connect((self.host, self.port))
                    s.sendall(message.encode('utf-8'))
                    response = self._receive_response(s)
                    return response
            except (ConnectionRefusedError, socket.timeout, OSError) as e:
                print(f"Connection error: {e}. Retrying in {delay} seconds... (Attempt {attempt + 1}/{retries})")
                time.sleep(delay)
        print(f"Failed to connect to server after {retries} attempts.")
        return None



    def _receive_response(self, sock: socket.socket) -> Optional[Dict[str, Any]]:
            """
            Receive full response until newline terminator, with robust UTF-8 fallback.
            Handles large responses and invalid UTF-8 bytes (common in widget data).
            """
            data = b''
            while True:
                try:
                    part = sock.recv(4096)
                    if not part:
                        break
                    data += part
                    if b'\n' in data:
                        break
                except socket.timeout:
                    print("Socket timeout while receiving response.")
                    return None

            if not data:
                print("No data received from server.")
                return None

            # Split on first newline (server terminates with \n)
            if b'\n' in data:
                response_bytes = data.split(b'\n', 1)[0]
            else:
                response_bytes = data  # Fallback if no newline

            # Robust decoding: Try UTF-8, fallback to latin-1 (maps all bytes, no error)
            try:
                response_str = response_bytes.decode('utf-8')
            except UnicodeDecodeError:
                response_str = response_bytes.decode('latin-1')

            response_str = response_str.strip()

            # Optional debug for large responses

            try:
                return json.loads(response_str)
            except json.JSONDecodeError as e:
                print(f"Failed to parse JSON response: {e}")
                print(f"Response preview (first 500 chars): {response_str[:500]}")
                return None

    def fetch_bank_items(self) -> Optional[List[Dict[str, Any]]]:
        """
        Fetch cached bank items from the local JSON file (faster than socket request).

        Returns:
            Optional[List[Dict[str, Any]]]: List of bank items ({'id': int, 'quantity': int, 'slot': int}) or None if error/file missing.
        """
        file_path = r"C:\Users\Asd\source\repos\runelite_plugin\modules\fetch_data\bank\bank_items.json"
        try:
            with open(file_path, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error fetching cached bank items: {e}")
            return None

    def player(self, location: bool = True, health: bool = True, prayer: bool = True, run: bool = True,
               weight: bool = True, animation: bool = True, camera: bool = True) -> Optional[Dict[str, Any]]:
        """
        Retrieve player data from the plugin server, including Varbits if requested.

        Args:
            location (bool): Include player location.
            health (bool): Include player health.
            prayer (bool): Include prayer points (and Varbits if supported).
            run (bool): Include run energy.
            weight (bool): Include player weight.
            animation (bool): Include player animation.
            camera (bool): Include camera information.

        Returns:
            Optional[Dict[str, Any]]: Player data or None if request fails.
        """
        params = {
            'location': location,
            'health': health,
            'prayer': prayer,
            'run': run,
            'weight': weight,
            'animation': animation,
            'camera': camera
        }
        return self.send_request('player', params)

    def quest(self) -> Optional[Dict[str, Any]]:
        """
        Retrieve quest states from the plugin server.

        Returns:
            Optional[Dict[str, Any]]: Quest data or None if request fails.
        """
        return self.send_request('quest', {})

    def stats(self) -> Optional[Dict[str, Any]]:
        """
        Retrieve skill levels and XP from the plugin server.

        Returns:
            Optional[Dict[str, Any]]: Stats data or None if request fails.
        """
        return self.send_request('stats', {})

    def gear(self) -> Optional[Dict[str, Any]]:
        """
        Retrieve equipped gear from the plugin server.

        Returns:
            Optional[Dict[str, Any]]: Gear data or None if request fails.
        """
        return self.send_request('gear', {})

    def chat(self) -> Optional[Dict[str, Any]]:
        """
        Retrieve recent chat messages from the plugin server.

        Returns:
            Optional[Dict[str, Any]]: Chat data or None if request fails.
        """
        return self.send_request('chat', {})

    def npc(self, id: str = "", name: str = "", tile: bool = True, middle_point: bool = True,
            animation: bool = True, size: bool = True, in_combat: Optional[bool] = None) -> Optional[Dict[str, Any]]:
        """
        Retrieve NPC data from the plugin server.

        Args:
            id (str): Filter by NPC ID.
            name (str): Filter by NPC name.
            tile (bool): Include NPC tile location.
            middle_point (bool): Include NPC screen middle point.
            animation (bool): Include NPC animation.
            size (bool): Include NPC size.
            in_combat (Optional[bool]): Filter by combat status.

        Returns:
            Optional[Dict[str, Any]]: NPC data or None if request fails.
        """
        params = {
            'id': id,
            'name': name,
            'tile': tile,
            'middle_point': middle_point,
            'animation': animation,
            'size': size,
            'in_combat': in_combat
        }
        return self.send_request('npc', params)
    
    def inventory(self, item: str = "", middle_point: bool = True) -> Optional[Dict[str, Any]]:
        params = {
            'item': item,
            'middle_point': middle_point
        }
        inventory_data = self.send_request('inventory', params)
        if not inventory_data or 'data' not in inventory_data or not inventory_data['data']:
            return inventory_data

        if middle_point:
            modified_data = []
            for item_data in inventory_data['data']:
                modified_item = item_data.copy()
                if 'middle_point' in item_data:
                    if 'random_clickpoint' not in item_data:
                        x = item_data['middle_point']['x']
                        y = item_data['middle_point']['y']
                        random_clickpoint = {
                            'x': x + random.randint(-8, 8),
                            'y': y + random.randint(-7, 7)
                        }
                        modified_item['random_clickpoint'] = random_clickpoint
                modified_data.append(modified_item)
            return {'data': modified_data}

        return inventory_data

    def inventory_random_clickpoint(self, item: str = "") -> Optional[Dict[str, Any]]:
        """
        Retrieve inventory item data with a random click point offset from the middle point.

        Args:
            item (str): Filter by item name or ID.

        Returns:
            Optional[Dict[str, Any]]: Inventory data with a random click point or None if request fails.
        """
        inventory_data = self.inventory(item=item, middle_point=True)
        if not inventory_data or 'data' not in inventory_data or not inventory_data['data']:
            return inventory_data

        modified_data = []
        for item_data in inventory_data['data']:
            modified_item = item_data.copy()
            if 'middle_point' in item_data:
                x = item_data['middle_point']['x']
                y = item_data['middle_point']['y']
                random_clickpoint = {
                    'x': x + random.randint(0, 16),
                    'y': y + random.randint(0, 14)
                }
                modified_item['random_clickpoint'] = random_clickpoint
            modified_data.append(modified_item)

        return {'data': modified_data}

    def game_object(self, object: str = "", tile: bool = True, tile_radius: int = 6,
                    middle_point: bool = True) -> Optional[Dict[str, Any]]:
        """
        Retrieve game object data from the plugin server.

        Args:
            object (str): Filter by object name or ID.
            tile (bool): Include object tile location.
            tile_radius (int): Radius to search for objects.
            middle_point (bool): Include object screen middle point.

        Returns:
            Optional[Dict[str, Any]]: Game object data or None if request fails.
        """
        params = {
            'object': object,
            'tile': tile,
            'tile_radius': tile_radius,
            'middle_point': middle_point
        }
        return self.send_request('gameObject', params)

    def tile(self, tile_x: int, tile_y: int, tile_radius: int = 6,
             middle_point: bool = True) -> Optional[Dict[str, Any]]:
        """
        Retrieve tile data from the plugin server.

        Args:
            tile_x (int): X-coordinate of the tile.
            tile_y (int): Y-coordinate of the tile.
            tile_radius (int): Radius to search for tiles.
            middle_point (bool): Include tile screen middle point.

        Returns:
            Optional[Dict[str, Any]]: Tile data or None if request fails.
        """
        params = {
            'tile': {'x': tile_x, 'y': tile_y},
            'tile_radius': tile_radius,
            'middle_point': middle_point
        }
        return self.send_request('tile', params)

    def walkable_tile(self, tile_x: int, tile_y: int, tile_radius: int = 15,
                      middle_point: bool = True) -> Optional[Dict[str, Any]]:
        """
        Retrieve walkable tile data from the plugin server.

        Args:
            tile_x (int): X-coordinate of the tile.
            tile_y (int): Y-coordinate of the tile.
            tile_radius (int): Radius to search for walkable tiles.
            middle_point (bool): Include tile screen middle point.

        Returns:
            Optional[Dict[str, Any]]: Walkable tile data or None if request fails.
        """
        params = {
            'tile': {'x': tile_x, 'y': tile_y},
            'tile_radius': tile_radius,
            'middle_point': middle_point
        }
        return self.send_request('walkable_tile', params)

    def gametick(self) -> Optional[Dict[str, Any]]:
        """
        Retrieve current game tick from the plugin server.

        Returns:
            Optional[Dict[str, Any]]: Game tick data or None if request fails.
        """
        return self.send_request('gametick', {})

    def interact_options(self) -> Optional[Dict[str, Any]]:
        """
        Retrieve interaction options from the plugin server.

        Returns:
            Optional[Dict[str, Any]]: Interaction options data or None if request fails.
        """
        return self.send_request('interactOptions', {})

    def pick(self, x: int, y: int, size: int = 0, item: str = "") -> Optional[Dict[str, Any]]:
        """
        Retrieve ground item data for picking up from the plugin server.

        Args:
            x (int): X-coordinate of the center tile.
            y (int): Y-coordinate of the center tile.
            size (int): Size of the area to search.
            item (str): Name of the item to pick up.

        Returns:
            Optional[Dict[str, Any]]: Ground item data or None if request fails.
        """
        params = {
            'x': x,
            'y': y,
            'size': size,
            'item': item
        }
        return self.send_request('pick', params)

    def minimap_tiles(self, tilex: Optional[int] = None, tiley: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Retrieve minimap tile data from the plugin server.

        Args:
            tilex (Optional[int]): X-coordinate of a specific tile.
            tiley (Optional[int]): Y-coordinate of a specific tile.

        Returns:
            Optional[Dict[str, Any]]: Minimap tile data or None if request fails.
        """
        params = {}
        if tilex is not None and tiley is not None:
            params['tilex'] = tilex
            params['tiley'] = tiley
        return self.send_request('minimapTiles', params)

    def minimap_tile_point(self, tile_x: int, tile_y: int, plane: Optional[int] = None) -> Optional[Dict[str, Any]]:
            """
            Fetch the clickable screen point on the minimap for a given world tile, handling zoomed out state.

            Args:
                tile_x (int): World X coordinate.
                tile_y (int): World Y coordinate.
                plane (Optional[int]): World plane (defaults to current player plane).

            Returns:
                Optional[Dict[str, Any]]: {'x': int, 'y': int} for the canvas point, or None if failed/unreachable.
            """
            params = {'x': tile_x, 'y': tile_y}
            if plane is not None:
                params['plane'] = plane
            return self.send_request('minimapTilePoint', params)

    def main_menu(self) -> Optional[Dict[str, Any]]:
        """
        Retrieve main menu data, including world list, from the plugin server.

        Returns:
            Optional[Dict[str, Any]]: Main menu data or None if request fails.
        """
        return self.send_request('mainMenu', {})

    def bank_items(self, item: str = "") -> Optional[Dict[str, Any]]:
        """
        Retrieve bank item data from the plugin server with optional filtering.

        Args:
            item (str): Filter by item name or ID.

        Returns:
            Optional[Dict[str, Any]]: Bank item data or None if request fails.
        """
        params = {'item': item}
        return self.send_request('bankItems', params)

    def bank_interface(self) -> Optional[Dict[str, Any]]:
        """
        Retrieve bank interface widget data from the plugin server.

        Returns:
            Optional[Dict[str, Any]]: Bank interface data or None if request fails.
        """
        return self.send_request('bankInterface', {})

    def game_state(self) -> Optional[str]:
        """
        Retrieve the current game state from the plugin server.

        Returns:
            Optional[str]: Game state name or None if request fails.
        """
        return self.send_request('gameState', {})

    def bank(self, deposit_inventory: bool = False, deposit_equipment: bool = False, placeholder: bool = False,
             noted: bool = False, withdraw_1: bool = False, withdraw_5: bool = False, withdraw_10: bool = False,
             withdraw_x: bool = False, withdraw_all: bool = False, deposit: str = None, withdraw: str = None,
             quantity: str = None) -> Optional[Dict[str, Any]]:
        """
        Retrieve bank button states and handle deposit/withdraw actions.

        Args:
            deposit_inventory (bool): Check deposit inventory button state.
            deposit_equipment (bool): Check deposit equipment button state.
            placeholder (bool): Check placeholder button state.
            noted (bool): Check noted (itemButton) button state.
            withdraw_1 (bool): Check withdraw 1 button state.
            withdraw_5 (bool): Check withdraw 5 button state.
            withdraw_10 (bool): Check withdraw 10 button state.
            withdraw_x (bool): Check withdraw X button state.
            withdraw_all (bool): Check withdraw all button state.
            deposit (str): Item to deposit (optional).
            withdraw (str): Item to withdraw (optional).
            quantity (str): Quantity to withdraw/deposit (e.g., "1", "5", "10", "x", "all", optional).

        Returns:
            Optional[Dict[str, Any]]: Bank data including button states and action data or None if request fails.
        """
        params = {
            "depositInvButton": deposit_inventory,
            "depositEquipmentButton": deposit_equipment,
            "placeholderButton": placeholder,
            "itemButton": noted,
            "withdraw1Button": withdraw_1,
            "withdraw5Button": withdraw_5,
            "withdraw10Button": withdraw_10,
            "withdrawXButton": withdraw_x,
            "withdrawAllButton": withdraw_all,
            "deposit": deposit,
            "withdraw": withdraw,
            "quantity": quantity
        }
        return self.send_request('bank', params)

    def get_active_prayers(self) -> Optional[Dict[str, bool]]:
        """
        Retrieve the active status of all prayers from the plugin server.

        Returns:
            Optional[Dict[str, bool]]: Dictionary mapping prayer names to their active status, or None if failed.
        """
        return self.send_request('prayers', {})

    def attack_style(self) -> Optional[Dict[str, Any]]:
        """
        Retrieve the player's CURRENT ATTACK STYLE with full details.
        
        Returns:
            Optional[Dict[str, Any]]: {
                'data': {
                    'style': 'AGGRESSIVE' | 'ACCURATE' | 'RAPID' | 'LONGRANGE' | 
                             'CASTING' | 'DEFENSIVE_CASTING' | 'OTHER',
                    'name': 'Aggressive' | 'Accurate' | ... (human readable),
                    'styleIndex': int,
                    'weaponCategory': int,
                    'defensiveCasting': bool
                }
            }
        """
        return self.send_request('attack_style', {})

    def npc_agro(self, name: str = "") -> Optional[Dict[str, Any]]:
        """
        Retrieve data about aggressive NPCs from the plugin server.

        Args:
            name (str): Optional NPC name to filter by (case-insensitive).

        Returns:
            Optional[Dict[str, Any]]: Aggressive NPC data or None if request fails.
            - If name is provided, returns data for the specific NPC (aggressive status, name, id, health, location,
              onCooldown, cooldownRemaining, attackSpeed, canReach).
            - If no name is provided, returns a list of all aggressive NPCs with their details.
        """
        params = {'name': name} if name else {}
        response = self.send_request('npc_agro', params)
        if response and 'data' in response:
            data = response['data']
            if name:
                if data.get('aggressive', False):
                    print(f"NPC: {data['name']} (ID: {data['id']}) is aggressive.")
                    status = "green" if data['canReach'] and not data['onCooldown'] else "red"
                    print(f"Status: {status} (Can Reach: {data['canReach']}, On Cooldown: {data['onCooldown']}, "
                          f"Cooldown Remaining: {data['cooldownRemaining']} ticks)")
                else:
                    print(f"NPC: {name} is not aggressive.")
            else:
                aggressive_npcs = data.get('aggressiveNpcs', [])
                if aggressive_npcs:
                    print("Aggressive NPCs:")
                    for npc in aggressive_npcs:
                        status = "green" if npc['canReach'] and not npc['onCooldown'] else "red"
                        print(f"- {npc['name']} (ID: {npc['id']}): Status: {status}, "
                              f"Can Reach: {npc['canReach']}, On Cooldown: {npc['onCooldown']}, "
                              f"Cooldown Remaining: {npc['cooldownRemaining']} ticks")
                else:
                    print("No aggressive NPCs found.")
            return data
        print("Failed to retrieve NPC aggression data.")
        return None
    
    def logout_widgets(self) -> Optional[Dict[str, Any]]:
        """
        Retrieve logout screen widgets data (positions, sizes, etc.) from the plugin server.
        Returns:
            Optional[Dict[str, Any]]: Widgets data or None if request fails.
        """
        return self.send_request('logout', {})

    def varbit(self, varbit_id: int) -> Optional[int]:
        """
        Retrieve the value of a single Varbit from the plugin server.

        Args:
            varbit_id (int): The Varbit ID to query.

        Returns:
            Optional[int]: The Varbit value, or None if failed.
        """
        result = self.get_varbits([varbit_id])
        if result and 'data' in result and 'values' in result['data']:
            values = result['data']['values']
            return values.get(str(varbit_id))
        print(f"Failed to retrieve Varbit {varbit_id}. Response: {result}")
        return None
    
    def players(self, radius: int = 10, name: str = "") -> Optional[Dict[str, Any]]:
            """
            Retrieve data about other players within a specified tile radius from the local player.

            Args:
                radius (int): Tile radius to filter players (default: 10).
                name (str): Optional name filter (case-insensitive partial match).

            Returns:
                Optional[Dict[str, Any]]: {'data': list of player dicts} where each dict contains:
                    - name: str
                    - id: int
                    - combatLevel: int
                    - location: str (WorldPoint)
                    - animation: int
                    - healthRatio: int
                    - isInteracting: bool
                or None if request fails.
            """
            params = {'radius': radius}
            if name:
                params['name'] = name
            return self.send_request('players', params)

    def fetch_object(self, obj_id: str, action: str, tile_x: Optional[int] = None, tile_y: Optional[int] = None, radius: int = 20, middle_point: bool = True) -> Optional[Dict[str, Any]]:
        """
        Retrieve local object data matching the ID and action, either on a specific tile or within a radius around the player.

        Args:
            obj_id (str): The object ID to filter by.
            action (str): The action (e.g., 'Open') to filter by.
            tile_x (Optional[int]): The X coordinate of the specific tile (if provided, searches only this tile).
            tile_y (Optional[int]): The Y coordinate of the specific tile (if provided, searches only this tile).
            radius (int): The search radius around the player if no tile is provided (default: 20).
            middle_point (bool): Include screen middle point (default: True).

        Returns:
            Optional[Dict[str, Any]]: Object data or None if request fails.
        """
        params = {
            'id': obj_id,
            'action': action,
            'middle_point': middle_point
        }
        if tile_x is not None and tile_y is not None:
            params['tile'] = {'x': tile_x, 'y': tile_y}
        else:
            params['radius'] = radius
        return self.send_request('local_object', params)

    def target_npc() -> Optional[Dict[str, Any]]:
        """
        Retrieve the exact NPC the player is currently attacking/interacting with.
        Returns a dict with:
            - name
            - id
            - index (unique per spawn)
            - healthRatio / healthScale
            - animation
            - location (world coords)
            - middle_point (canvas coordinates for direct clicking)
        or None if no target.
        """
        return _default_client.send_request('target_npc', {})

    def cannon_data(self) -> Optional[Dict[str, Any]]:
        """Get data about your own cannon (position, id, ammo, exists)."""
        return self.send_request('cannon_data', {})

    def reset_cannon(self):
        """Manually reset cannon tracking (useful for debugging or after pickup)."""
        return self.send_request('reset_cannon', {})

    def get_var(self, var_id: int) -> Optional[Dict[str, Any]]:
        """Single ID query across Varbit, Varp, VarClientInt."""
        return self.send_request('get_varbits', {'id': var_id})

    def get_varbits(self, varbit_ids: List[int]) -> Optional[Dict[str, Any]]:
        """Bulk Varbit query (backward compatible)."""
        params = {str(id): 0 for id in varbit_ids}
        return self.send_request('get_varbits', params)
        
    def grand_exchange(self) -> Optional[Dict[str, Any]]:
        """
        Retrieve ALL Grand Exchange offers (8 slots) with full details.

        Returns:
            Optional[Dict[str, Any]]: {
                'offers': list of dicts (one per slot),
                'totalSlots': 8,
                'activeOffers': int
            }
            Each offer dict contains:
                slot, state, itemId, itemName, quantitySold, totalQuantity,
                price, spent, isBuyOffer, isEmpty, isComplete, isCancelled, progressPercent
        """
        return self.send_request('grand_exchange', {})
    def combat_style(self) -> Optional[Dict[str, Any]]:
        """Deprecated alias — use attack_style() instead."""
        return self.attack_style()

_default_client = PluginClient(auth_token='jQ8IHav3zA3HuH4')

# ==================== NEW ATTACK STYLE WRAPPERS ====================

def attack_style() -> Optional[Dict[str, Any]]:
    """
    Get current attack style (Accurate, Aggressive, Rapid, Longrange, Casting, Defensive Casting, etc.)
    Returns the full rich dict or None.
    """
    return _default_client.attack_style()

def get_attack_style_name() -> str:
    """Quick way to get just the readable name (e.g. "Aggressive")."""
    response = attack_style()
    if response and 'data' in response and 'name' in response['data']:
        return response['data']['name']
    return "Unknown"

def get_attack_style_enum() -> str:
    """Quick way to get the enum style (e.g. "AGGRESSIVE")."""
    response = attack_style()
    if response and 'data' in response and 'style' in response['data']:
        return response['data']['style']
    return "OTHER"

# Keep your old combat_style wrapper for backward compatibility
def combat_style() -> Optional[Dict[str, Any]]:
    """Old simple combat style (kept for backward compatibility) — calls WeaponHandler."""
    return _default_client.send_request('combat_style', {})

def grand_exchange() -> Optional[Dict[str, Any]]:
    """Retrieve Grand Exchange offers (convenience wrapper)."""
    return _default_client.grand_exchange()

def get_var(var_id: int) -> Optional[Dict[str, Any]]:
    return _default_client.get_var(var_id)

def get_varbits(varbit_ids: List[int]) -> Optional[Dict[str, Any]]:
    return _default_client.get_varbits(varbit_ids)

def slayer_task_remaining() -> int:
    """Get the number of NPCs left to kill in your current Slayer task."""
    response = _default_client.send_request('slayer_task_remaining', {})
    return response.get('data', 0) if response else 0

def varbit_changes() -> Optional[List[Dict[str, Any]]]:
    """
    Get list of variable changes since last call (for debugging).
    Each change dict now includes:
    - 'type': str ('varbit', 'varp', 'varcint', 'varcstr')
    - 'id': int
    - 'old': int/str (depending on type; -1 or '' if unknown)
    - 'new': int/str
    - 'tick': int
    """
    return _default_client.send_request('varbit_changes', {})

def cannon_data(): return _default_client.cannon_data()

def reset_cannon():
    """Manually reset cannon tracking (useful if detection failed)."""
    return _default_client.send_request('reset_cannon', {})

def target_npc() -> Optional[Dict[str, Any]]:
    """Retrieve the NPC the player is currently interacting with/attacking."""
    return _default_client.send_request('target_npc', {})

def fetch_object(obj_id: str, action: str, tile_x: Optional[int] = None, tile_y: Optional[int] = None, radius: int = 20, middle_point: bool = True) -> Optional[Dict[str, Any]]:
    """Retrieve local object data matching the ID and action."""
    return _default_client.fetch_object(obj_id, action, tile_x, tile_y, radius, middle_point)

def players(radius: int = 10, name: str = "") -> Optional[Dict[str, Any]]:
    """
    Retrieve data about other players within a specified tile radius.
    """
    return _default_client.players(radius, name)

def varbit(varbit_id: int) -> Optional[int]:
    """Retrieve the value of a single Varbit from the plugin server."""
    return _default_client.varbit(varbit_id)

def fetch_bank_items() -> Optional[List[Dict[str, Any]]]:
    """Fetch cached bank items from file."""
    return _default_client.fetch_bank_items()

def logout_widgets() -> Optional[Dict[str, Any]]:
    """Retrieve logout screen widgets data."""
    return _default_client.logout_widgets()

def quest() -> Optional[Dict[str, Any]]:
    """Retrieve quest states."""
    return _default_client.quest()

def stats() -> Optional[Dict[str, Any]]:
    """Retrieve skill levels and XP."""
    return _default_client.stats()

def gear() -> Optional[Dict[str, Any]]:
    """Retrieve equipped gear."""
    return _default_client.gear()

def chat() -> Optional[Dict[str, Any]]:
    """Retrieve recent chat messages."""
    return _default_client.chat()

def npc(id: str = "", name: str = "", tile: bool = True, middle_point: bool = True,
        animation: bool = True, size: bool = True, in_combat: Optional[bool] = None) -> Optional[Dict[str, Any]]:
    """Retrieve NPC data."""
    return _default_client.npc(id, name, tile, middle_point, animation, size, in_combat)

def inventory(item: str = "", middle_point: bool = True) -> Optional[Dict[str, Any]]:
    """Retrieve inventory item data with a random click point offset."""
    return _default_client.inventory(item, middle_point)

def inventory_random_clickpoint(item: str = "") -> Optional[Dict[str, Any]]:
    """Retrieve inventory item data with a random click point offset from the middle point."""
    return _default_client.inventory_random_clickpoint(item)

def game_object(object: str = "", tile: bool = True, tile_radius: int = 6,
                middle_point: bool = True) -> Optional[Dict[str, Any]]:
    """Retrieve game object data."""
    return _default_client.game_object(object, tile, tile_radius, middle_point)

def player(location: bool = True, health: bool = True, prayer: bool = True, run: bool = True,
           weight: bool = True, animation: bool = True, camera: bool = True) -> Optional[Dict[str, Any]]:
    """Retrieve player data."""
    return _default_client.player(location, health, prayer, run, weight, animation, camera)

def tile(tile_x: int = 0, tile_y: int = 0, tile_radius: int = 6,
         middle_point: bool = True) -> Optional[Dict[str, Any]]:
    """Retrieve tile data."""
    return _default_client.tile(tile_x, tile_y, tile_radius, middle_point)

def walkable_tile(tile_x: int = 0, tile_y: int = 0, tile_radius: int = 0,
                  middle_point: bool = True) -> Optional[Dict[str, Any]]:
    """Retrieve walkable tile data."""
    return _default_client.walkable_tile(tile_x, tile_y, tile_radius, middle_point)

def gametick() -> Optional[Dict[str, Any]]:
    """Retrieve current game tick."""
    return _default_client.gametick()

def interact_options() -> Optional[Dict[str, Any]]:
    """Retrieve interaction options."""
    return _default_client.interact_options()

def pick(x: int, y: int, size: int = 0, item: str = "") -> Optional[Dict[str, Any]]:
    """Retrieve ground item data for picking up."""
    return _default_client.pick(x, y, size, item)

def minimap_tiles(tilex: Optional[int] = None, tiley: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """Retrieve minimap tile data."""
    return _default_client.minimap_tiles(tilex, tiley)

def main_menu() -> Optional[Dict[str, Any]]:
    """Retrieve main menu data, including world list."""
    return _default_client.main_menu()

def bank_items(item: str = "") -> Optional[Dict[str, Any]]:
    """Retrieve bank item data with optional filtering."""
    return _default_client.bank_items(item)

def game_state() -> Optional[str]:
    """Retrieve current game state."""
    return _default_client.game_state()

def bank(deposit_inventory: bool = False, deposit_equipment: bool = False, placeholder: bool = False,
         noted: bool = False, withdraw_1: bool = False, withdraw_5: bool = False, withdraw_10: bool = False,
         withdraw_x: bool = False, withdraw_all: bool = False, deposit: str = None, withdraw: str = None,
         quantity: str = None) -> Optional[Dict[str, Any]]:
    """Retrieve bank button states and handle deposit/withdraw actions."""
    return _default_client.bank(deposit_inventory, deposit_equipment, placeholder, noted, withdraw_1, withdraw_5,
                               withdraw_10, withdraw_x, withdraw_all, deposit, withdraw, quantity)

def get_active_prayers() -> Optional[Dict[str, bool]]:
    """
    Retrieve the active status of all prayers from the plugin server.

    Returns:
        Optional[Dict[str, bool]]: Dictionary mapping prayer names to their active status, or None if failed.
    """
    return _default_client.get_active_prayers()

def npc_agro(name: str = "") -> Optional[Dict[str, Any]]:
    """
    Retrieve data about aggressive NPCs from the plugin server.

    Args:
        name (str): Optional NPC name to filter by (case-insensitive).

    Returns:
        Optional[Dict[str, Any]]: Aggressive NPC data or None if request fails.
    """
    return _default_client.npc_agro(name)

def minimap_tile_point(tile_x: int, tile_y: int, plane: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """Fetch the clickable screen point on the minimap for a given world tile, handling zoomed out state."""
    return _default_client.minimap_tile_point(tile_x, tile_y, plane)

