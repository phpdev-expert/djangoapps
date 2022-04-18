from django.conf.urls import url
from .views import AccountManagerAPIView

urlpatterns = [
    url(r'', AccountManagerAPIView)
]
