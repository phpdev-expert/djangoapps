import os

from celery import Celery
from django.conf import settings


# set the default Django settings module for the 'celery' program.
if not os.environ.get('DJANGO_SETTINGS_MODULE', None):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webapp.conf.local')


app = Celery('webapp', broker=settings.CELERY_BROKER_URL)
app.config_from_object('django.conf:settings')
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))