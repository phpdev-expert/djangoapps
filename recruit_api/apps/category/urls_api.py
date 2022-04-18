from django.conf.urls import url
from .views_api.category import CategoryView
from rest_framework.routers import DefaultRouter
from django.urls import include, path

router = DefaultRouter()
router.register('', CategoryView)

urlpatterns = [
        path('', include(router.urls)),
]
