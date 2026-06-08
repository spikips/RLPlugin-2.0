from modules.core.plugin_client import _default_client
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

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
    
def get_widget_by_id(widget_id: int):
    """
    Get data for a SINGLE widget by its ID.
    Strong debug version to see exactly what is being sent.
    """
    params = {'id': widget_id}
    # print(f"🔍 [DEBUG] get_widget_by_id({widget_id}) → sending params: {params}")

    response = _default_client.send_request("clickWidget", params)

    if not response:
        print(f"❌ No response for widget {widget_id}")
        return None

    # print(f"📥 [DEBUG] Received raw response type: {type(response)} | keys: {list(response.keys()) if isinstance(response, dict) else 'N/A'}")

    try:
        data = json.loads(response) if isinstance(response, str) else response
        if not isinstance(data, dict):
            return None

        # Case 1: New fast path
        if 'widgets' in data and data['widgets']:
            widget = data['widgets'][0]
            if isinstance(widget, dict) and widget.get("id") == widget_id:
                # print(f"✅ FAST PATH SUCCESS - widget {widget_id} found")
                return widget

        # Case 2: Wrapped response (SocketServer adds 'data')
        if 'data' in data:
            inner = data['data']
            if isinstance(inner, dict) and 'widgets' in inner and inner['widgets']:
                widget = inner['widgets'][0]
                if isinstance(widget, dict) and widget.get("id") == widget_id:
                    # print(f"✅ FAST PATH SUCCESS (wrapped) - widget {widget_id} found")
                    return widget

        print(f"⚠️ Widget {widget_id} not found in response")
        return None
    except Exception as e:
        print(f"Failed to parse widget {widget_id}: {e}")
        return None