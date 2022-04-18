from django.conf.urls import url
from .views_api import email

urlpatterns = [
    url(r'', email.as_view())
]
