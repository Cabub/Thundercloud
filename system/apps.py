from django.apps import AppConfig


class SystemConfig(AppConfig):
    name = 'system'

    def ready(self):
        from . import signals
