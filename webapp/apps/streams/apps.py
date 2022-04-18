from django.apps import AppConfig


class StreamsConfig(AppConfig):
    name = 'webapp.apps.streams'

    def ready(self):
        import webapp.apps.streams.signals
        pass
