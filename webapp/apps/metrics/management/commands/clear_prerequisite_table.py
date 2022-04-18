from django.core.management.base import BaseCommand
from webapp.apps.metrics.models import Metrics, MetricsAttribute
from webapp.apps.reports.models import WidgetTemplate

class Command(BaseCommand):

    def handle(self, *args, **options):
        Metrics.objects.all().delete()
        MetricsAttribute.objects.all().delete()
        WidgetTemplate.objects.all().delete()


