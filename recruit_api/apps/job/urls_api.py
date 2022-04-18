from django.conf.urls import url
from .views_api.job import JobView
from .views_api.skill import SkillView
from rest_framework.routers import DefaultRouter
from django.urls import include, path

router = DefaultRouter()
router.register('', JobView)


urlpatterns = [
        path('', include(router.urls)),
]
