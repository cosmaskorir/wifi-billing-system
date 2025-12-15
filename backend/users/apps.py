from django.apps import AppConfig

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self):
        """
        This method runs when Django starts.
        We import the signals module here to ensure the Password Reset
        and Email logic is registered and listening for events.
        """
        import users.signals