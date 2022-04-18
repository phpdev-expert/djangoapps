import django_filters
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ModelViewSet
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from webapp.apps.api.serializers.posts import RecentPostSerializer
from webapp.apps.metrics.models import AccountObject
from webapp.base.base_api import BaseAPIView

import logging

log = logging.getLogger("webapp")


class RecentPostViewSet(BaseAPIView, ModelViewSet):
    queryset = AccountObject.objects.prefetch_related().filter().order_by("-date_posted")
    serializer_class = RecentPostSerializer
    http_method_names = ["get"]
    permission_classes = [AllowAny]
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    # filter_fields = ("limit",)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("limit", openapi.IN_QUERY, type=openapi.TYPE_STRING)
        ]
    )
    def list(self, request, *args, **kwargs):
        count = int(request.GET.get("limit", 1))
        auth_user = request.auth_user_id
        queryset = (AccountObject.objects.filter(
            account__user_id=auth_user,
            account__status__in=["active", "revoked"]
        ).prefetch_related("accountmetrics_set").order_by("-date_posted").exclude(date_posted=None))[:count]
        serializer = RecentPostSerializer(queryset, many=True)

        return Response(serializer.data, 200)