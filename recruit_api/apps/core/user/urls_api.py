from django.conf.urls import url
from .views_api import (authenticate_user, change_password, personal_info, user)
from .views_api.users import UserView
from rest_framework.routers import DefaultRouter
from django.urls import include, path
router = DefaultRouter()
router.register('', UserView)
urlpatterns = [
    path('', include(router.urls)),
]
