from django.apps import AppConfig


class ZzapCoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'zzap_core'

    def ready(self):
        from zzap_core import signals
