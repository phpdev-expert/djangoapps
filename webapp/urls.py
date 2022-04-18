from django.conf.urls import url
from django.conf import settings
from django.contrib import admin
from django.urls import path, include

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

import socket

hostname = socket.gethostname()
server = settings.SERVER if settings.SERVER else "dev"
schema_view = get_schema_view(
    openapi.Info(
        title="SMB2 Reporting API",
        default_version="v1",
        description="API Specifications",
        terms_of_service="",
        contact=openapi.Contact(email="test@gmail.com"),
    ),
    url="http://localhost:8000/"
    if server == "local"
    else f"https://smb2-analyze-backend-{server}.pyxispm.com/",
    validators=[],
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("grappelli/", include("grappelli.urls"), name="grappelli"),
    url(r"^admin/", admin.site.urls),
    url(r'^health-check/', include('health_check.urls')),
    url(r"^api/v1/", include("webapp.apps.api.urls_v1")),
    url(r"^api/v2/", include("webapp.apps.api.urls_v2")),
    url(
        r"^docs(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=None),
        name="schema-json",
    ),
    url(
        r"^docs/$",
        schema_view.with_ui("swagger", cache_timeout=None),
        name="schema-swagger-ui",
    ),
    url(
        r"^redoc/$",
        schema_view.with_ui("redoc", cache_timeout=None),
        name="schema-redoc",
    ),
]

# urlpatterns += [url(r'^silk/', include('silk.urls', namespace='silk'))]
