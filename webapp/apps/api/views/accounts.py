import django_filters
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from webapp.apps.api.serializers.accounts import AccountObjectSerializer
from webapp.apps.metrics.models import AccountObject
from webapp.base.base_api import BaseAPIView

import logging

log = logging.getLogger("webapp")


class AccountObjectViewSet(BaseAPIView, ModelViewSet):
    queryset = (
        AccountObject.objects.prefetch_related().filter().order_by("-date_posted")
    )
    serializer_class = AccountObjectSerializer
    http_method_names = ["get"]
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    # filter_fields = ("limit",)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("pageid", openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter(
                "object_type",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                helptext="post,video",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        auth_user = request.auth_user_id
        queryset = AccountObject.objects.filter(
            account__user_id=auth_user,
            account__page_id__in=request.page_ids,
            object_type=request.GET.get("object_type"),
        ).order_by("-date_posted")
        objects = AccountObjectSerializer(queryset, many=True).data
        return Response(objects, 200)
