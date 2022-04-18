from django.apps import AppConfig


class BaseConfig(AppConfig):
    name = "webapp.apps.base"

    def ready(self):
        pass
