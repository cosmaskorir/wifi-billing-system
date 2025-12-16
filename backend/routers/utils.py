import routeros_api
from django.conf import settings

def get_router_connection():
    """
    Establishes a connection to the MikroTik router using settings from settings.py.
    """
    # ⚠️ Ensure these variables exist in your settings.py
    # If using .env, ensure MIKROTIK_HOST, MIKROTIK_USER, MIKROTIK_PASSWORD are set.
    connection = routeros_api.RouterOsApiPool(
        host=getattr(settings, 'MIKROTIK_HOST', '192.168.88.1'),
        username=getattr(settings, 'MIKROTIK_USER', 'admin'),
        password=getattr(settings, 'MIKROTIK_PASSWORD', ''),
        port=8728,
        plaintext_login=True # Required for newer RouterOS versions
    )
    return connection

def get_live_usage(username):
    """
    Connects to MikroTik and fetches total bytes for a specific user's Simple Queue.
    Returns: Dictionary {'upload_mb': 0.0, 'download_mb': 0.0}
    """
    usage_data = {'upload_mb': 0.0, 'download_mb': 0.0}
    connection = None

    try:
        connection = get_router_connection()
        api = connection.get_api()
        
        # We assume the Simple Queue has the SAME NAME as the Username
        queues = api.get_resource('/queue/simple')
        user_queue = queues.get(name=username)
        
        if user_queue:
            # MikroTik returns string: "upload_bytes/download_bytes" (e.g., "15000/450000")
            bytes_str = user_queue[0].get('bytes', '0/0')
            upload_bytes, download_bytes = map(int, bytes_str.split('/'))
            
            # Convert bytes to Megabytes (1 MB = 1024 * 1024 bytes)
            usage_data['upload_mb'] = round(upload_bytes / (1024 * 1024), 2)
            usage_data['download_mb'] = round(download_bytes / (1024 * 1024), 2)
            
    except Exception as e:
        # In production, use logging instead of print
        print(f"Error fetching usage for {username}: {e}")
        
    finally:
        if connection:
            connection.disconnect()
            
    return usage_data

class RouterManager:
    """
    Helper class to perform administrative actions on the Router.
    Used when a user pays (Enable) or expires (Disable).
    """
    def __init__(self):
        try:
            self.connection = get_router_connection()
            self.api = self.connection.get_api()
            self.connected = True
        except Exception as e:
            print(f"Router Connection Failed: {e}")
            self.connected = False

    def enable_user(self, username):
        """Enable a PPPoE/Hotspot secret when payment is received."""
        if not self.connected: return False
        
        try:
            # 1. Enable the PPP Secret
            secrets = self.api.get_resource('/ppp/secret')
            user = secrets.get(name=username)
            if user:
                secrets.set(id=user[0]['id'], disabled='no')
                return True
        except Exception as e:
            print(f"Failed to enable user {username}: {e}")
        return False

    def disable_user(self, username):
        """Disable user and kick them offline when subscription expires."""
        if not self.connected: return False

        try:
            # 1. Disable the PPP Secret
            secrets = self.api.get_resource('/ppp/secret')
            user = secrets.get(name=username)
            if user:
                secrets.set(id=user[0]['id'], disabled='yes')
            
            # 2. Kick the active connection so they lose internet immediately
            active_connections = self.api.get_resource('/ppp/active')
            active_user = active_connections.get(name=username)
            if active_user:
                active_connections.remove(id=active_user[0]['id'])
                
            return True
        except Exception as e:
            print(f"Failed to disable user {username}: {e}")
        return False

    def close(self):
        """Close connection manually if needed."""
        if self.connected:
            self.connection.disconnect()