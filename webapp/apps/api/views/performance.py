from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from webapp.base.base_api import BaseAPIView
from webapp.apps.api.serializers.reports import PerformanceConfigPostSerializer
from webapp.apps.reports.models import PerformanceConfig
import logging


log = logging.getLogger("report")


class PostPerformanceViewSet(BaseAPIView, ModelViewSet):
    queryset = PerformanceConfig.objects.filter().order_by("-date_created")
    serializer_class = PerformanceConfigPostSerializer
    http_method_names = ["get", "post"]

    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data

        PerformanceConfig.objects.update_or_create(
            user_id=request.auth_user_id, platform=data.get("platform"), defaults={
                "page_ids": data.get("page_ids"),
                "slugs": data.get("slugs")
            }
        )

        return Response(data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("platform", openapi.IN_QUERY, type=openapi.TYPE_STRING)
        ]
    )
    def list(self, request, *args, **kwargs):
        platform = request.GET.get("platform")
        pcs = {
            "page_ids": [],
            "platform": "",
            "slugs": []
        }
        pc = PerformanceConfig.objects.filter(
            user_id=request.auth_user_id, platform=platform
        )
        if pc:
            pc = pc.first()
            pcs = PerformanceConfigPostSerializer(pc).data
        return Response(pcs, 200)
