from django.conf.urls import url
from .views_api import client

urlpatterns = [
    url(r'', client),
]
