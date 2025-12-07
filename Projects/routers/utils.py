import routeros_api

class RouterManager:
    def __init__(self, router_instance):
        self.connection = routeros_api.RouterOsApiPool(
            router_instance.ip_address,
            username=router_instance.username,
            password=router_instance.password,
            port=router_instance.api_port,
            plaintext_login=True
        )
        self.api = self.connection.get_api()

    def add_user(self, username, password, profile_speed):
        """Creates a Hotspot user on the router"""
        try:
            # 1. Create Profile (e.g. 5M)
            profiles = self.api.get_resource('/ip/hotspot/user/profile')
            profile_name = f"{profile_speed}Mbps_Plan"
            
            if not profiles.get(name=profile_name):
                profiles.add(name=profile_name, rate_limit=f"{profile_speed}M/{profile_speed}M")

            # 2. Create User
            users = self.api.get_resource('/ip/hotspot/user')
            
            # Remove old user if exists
            old_user = users.get(name=username)
            if old_user:
                users.remove(id=old_user[0]['id'])
                
            users.add(name=username, password=password, profile=profile_name)
        except Exception as e:
            print(f"MikroTik Error: {e}")
        finally:
            self.connection.disconnect()