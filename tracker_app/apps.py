from django.apps import AppConfig

class TrackerAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tracker_app'

    def ready(self):
        import tracker_app.signals
