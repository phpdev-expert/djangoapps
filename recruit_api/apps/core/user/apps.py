from django.apps import AppConfig


class AUserConfig(AppConfig):
    name = 'recruit_api.apps.core.user'
    verbose_name = "Users"

    def ready(self):
        from recruit_api.apps.core.user.signals import create_auth_token
