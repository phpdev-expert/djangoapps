from django.conf.urls import url
from .views_api.clients import ClientsView
from rest_framework.routers import DefaultRouter
from django.urls import include, path

router = DefaultRouter()
router.register('', ClientsView)


urlpatterns = [
        path('', include(router.urls)),
]
