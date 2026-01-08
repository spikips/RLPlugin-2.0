from modules.core.plugin_client import _default_client
import json


def get_all_widget_data():
    """
    Retrieve data for all visible widgets and their children.
    
    Returns:
        list: List of widget data dictionaries including ID, text, hasOnOpListener, enabled status, and children.
    """
    params = {}  # No specific coordinates, request all widgets
    response = _default_client.send_request("clickWidget", params)
    if not response:
        print("No response from clickWidget request")
        return []

    try:
        data = json.loads(response) if isinstance(response, str) else response
        if isinstance(data, dict) and 'data' in data and 'widgets' in data['data']:
            return data['data']['widgets']
        print(f"Invalid widget data format: {data}")
        return []
    except json.JSONDecodeError as e:
        print(f"Failed to parse widget data: {e}, Raw data: {response}")
        return []