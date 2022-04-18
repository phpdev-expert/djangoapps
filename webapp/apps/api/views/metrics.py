from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import django_filters

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from webapp.base.base_api import BaseAPIView
from webapp.apps.metrics.models import Account, Metrics, AccountMetrics
from webapp.apps.api.serializers.metrics import (
    MetricsGetSerializer,
    MetricGetFilterSerializer,
)
from webapp.apps.api.views.reports import MetricComputation

import logging

log = logging.getLogger("webapp")


# class MetricsInsightViewSet(BaseAPIView, ModelViewSet):
#     queryset = PageMetricsLifetime.objects.prefetch_related().filter(
#                 ).order_by('-date_created')
#     serializer_class = MetricsInsightSerializer

#     http_method_names = ['get']
#     permission_classes = [AllowAny]


class MetricsViewSet(BaseAPIView, ModelViewSet, MetricComputation):
    queryset = Metrics.objects.prefetch_related().filter().order_by("-date_created")
    serializer_class = MetricsGetSerializer
    http_method_names = ["get"]
    permission_classes = [AllowAny]
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filter_fields = ("platform",)
    lookup_field = "slug"

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("platform", openapi.IN_QUERY, type=openapi.TYPE_STRING)
        ]
    )
    def retrieve(self, request, *args, **kwargs):
        output = []
        auth_user = request.auth_user_id
        serializer = MetricGetFilterSerializer(data=request.GET)
        serializer.is_valid(raise_exception=True)
        data = serializer.data

        params = {
            "account__user_id": str(auth_user),
            "metrics__platform": data["platform"],
            "metrics__slug": kwargs["slug"],
            # 'date':None,
            "object_id": None,
        }
        if request.page_ids:
            params["account__page_id__in"] = request.page_ids

        account_metrics = AccountMetrics.objects.filter(**params)
        account_metrics_mapping = self.get_metrics_mapping(account_metrics)
        _pages = list(
            Account.objects.filter(
                page_id__in=list(account_metrics_mapping.keys())
            ).values("page_id", "name")
        )
        pages = {p["page_id"]: p["name"] for p in _pages}
        for page_id, metrics in account_metrics_mapping.items():
            for m in metrics:
                tmp = {
                    "value": m["value"],
                    "date": m["date"],
                    "slug": m["slug"],
                    "page": {"id": page_id, "name": pages.get(page_id)},
                }
                output.append(tmp)

        return Response(output, 200)
