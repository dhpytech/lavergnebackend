from django.apps import AppConfig
import entries

class EntriesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'entries'

    def ready(self):
        import entries.signals
