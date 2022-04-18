from django.apps import AppConfig


class MetricsConfig(AppConfig):
    name = 'webapp.apps.metrics'

    def ready(self):
        import webapp.apps.metrics.signals
        pass