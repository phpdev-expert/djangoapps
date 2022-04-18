from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from webapp.base.base_api import BaseAPIView
from webapp.apps.reports.models import Reports, UserReportMapping, Widget
from webapp.apps.metrics.models import Account
from webapp.apps.api.views.metrics_v2 import MetricComputation
from webapp.apps.api.serializers.reports import (
    ReportSerializer,
    ReportGetRequestSerializer,
    WidgetSerializer,
    WidgetPostListSerializer,
    ReportWidgetSerializer,
)
import logging

log = logging.getLogger("report")

CUSTOM_METRICS = {
    "pageComment": {"type": "kv", "slug": "pageEngagementByType", "key": "comment"},
    "messageCount": {},
    "messages": {},
}


class ReportsViewSet(BaseAPIView, ModelViewSet):
    queryset = Reports.objects.prefetch_related().filter().order_by("-date_created")
    serializer_class = ReportSerializer

    def get_queryset(self):
        if len(self.request.page_ids) == 0:
            raise Exception("PAGEID is required in header")
        return (
            Reports.objects.prefetch_related()
            .filter(
                id__in=(
                    UserReportMapping.objects.filter(
                        user_id=self.request.auth_user_id,
                        page_id__in=self.request.page_ids,
                    ).values_list("report_id", flat=True)
                )
            )
            .order_by("-date_created")
        )

    def _filter_queryset(self, queryset, params):
        if "since" in params:
            queryset = queryset.filter(date__gte=params["since"])
        if "until" in params:
            queryset = queryset.filter(date__lte=params["until"])
        return queryset

    def prepare_widgets(self, report, data):
        widgets = list()


        for w in report.widgets.all():
            widget_slug = w.type
            _data = {
                "breakdown": w.breakdown,
                "platform": [w.platform],
                "aggregration": "As is",
            }
            print("report", _data)
            if "since" in data:
                _data["since"] = data["since"]

            if "until" in data:
                _data["until"] = data["until"]

            log.info("widget_slug : {}".format(widget_slug))
            filter_slugs, custom_slugs, agg_post, attributes_dict = MetricComputation.get_slugs(
                widget_slug, _data
            )
            log.info("slugs {} , {}".format(filter_slugs, custom_slugs))
            ##filter the pages based on widget platform
            pages = Account.objects.filter(
                user_id=self.request.auth_user_id, page_id__in=self.request.page_ids, type=w.platform
            ).values_list('page_id',flat=True )
            metric = MetricComputation.get_metrics(
                (filter_slugs, custom_slugs, agg_post),
                _data,
                self.request.auth_user_id,
                list(pages),
            )
            widgets.append(
                {
                    "id": w.id,
                    "platform": w.platform,
                    "type": w.type,
                    "style": w.style,
                    "breakdown": w.breakdown,
                    "aggregration": w.aggregration,
                    "metric": metric,
                    "attributes": attributes_dict,
                }
            )
        return widgets

    def prepare_report(self, page_ids, report, data):

        widgets = self.prepare_widgets(report, data)
        report = {
            "report_id": report.id,
            "platform": report.platform,
            "widgets": widgets,
        }
        return report

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("pageid", openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter("period", openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter(
                "since",
                openapi.IN_QUERY,
                type=openapi.FORMAT_DATETIME,
                format="yyyy-mm-dd",
            ),
            openapi.Parameter(
                "until",
                openapi.IN_QUERY,
                type=openapi.FORMAT_DATETIME,
                format="yyyy-mm-dd",
            ),
        ]
    )
    def retrieve(self, request, *args, **kwargs):
        output = []

        report = self.get_object()

        serializer = ReportGetRequestSerializer(data=request.GET)
        serializer.is_valid(raise_exception=True)

        data = serializer.data
        output = self.prepare_report(request.page_ids, report, data)
        return Response(output, 200)

    def list(self, request, *args, **kwargs):
        """
        List all reports
        """
        output = []
        queryset = (
            Reports.objects.prefetch_related()
            .filter(
                id__in=(
                    UserReportMapping.objects.filter(
                        user_id=self.request.auth_user_id
                    ).values_list("report_id", flat=True)
                )
            )
            .order_by("-date_created")
        )

        for q in queryset:
            page_ids = list(q.report_map.all().values_list("page_id", flat=True))
            output.append(
                {
                    "id": q.id,
                    "title": q.title,
                    "platform": q.platform,
                    "page_ids": page_ids,
                }
            )
        return Response(output, 200)

    def destroy(self, request, *args, **kwargs):
        instance = UserReportMapping.objects.filter(
            user_id=self.request.auth_user_id, report_id=kwargs["pk"]
        )
        if not instance:
            return Response("No such report with id {}".format(kwargs["pk"]), status=status.HTTP_404_NOT_FOUND)
        instance.delete()
        return Response("Report Deleted", status=status.HTTP_200_OK)


class GetReportViewSet(BaseAPIView, ModelViewSet):
    queryset = Reports.objects.prefetch_related().filter().order_by("-date_created")
    serializer_class = ReportSerializer
    permission_classes = []
    http_method_names = ["get"]


class ReportWidgetViewSet(ModelViewSet):
    queryset = Widget.objects.filter().order_by("-date_created")
    serializer_class = WidgetSerializer

    http_method_names = ["get", "post", "delete"]
    # lookup_field = "id"

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        if self.request.method == "POST":
            serializer_class = WidgetPostListSerializer
        return serializer_class(*args, **kwargs)

    def create(self, request, *args, **kwargs):
        data = request.data
        data["report_id"] = kwargs["report_pk"]
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        for order, widget in enumerate(data["widgets"]):
            breakdown = widget["breakdown"]
            aggregration = widget.get("aggregration", None)
            style = widget["style"]
            widget_id = widget.get("id", False)
            if widget_id:
                try:
                    w = Widget.objects.get(id=widget_id)
                except:  # noqa E722
                    raise Exception("Widget not found")
                else:
                    w.type = widget["type"]
                    w.style = style
                    w.order = order
                    w.breakdown = breakdown
                    w.aggregration = aggregration
                    w.save()
            else:
                Widget.objects.create(
                    report_id=kwargs["report_pk"],
                    type=widget["type"],
                    platform=widget["platform"],
                    breakdown=breakdown,
                    order=order,
                    aggregration=aggregration,
                    style=style,
                )

        headers = self.get_success_headers(serializer.data)
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)

    def list(self, request, *args, **kwargs):
        """
        List all widgets included in a report
        """
        rr = Reports.objects.filter(id=kwargs["report_pk"])
        widgets = rr.first().widgets.all()
        data = ReportWidgetSerializer(widgets, many=True).data
        return Response(data, 200)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response("Widget Deleted", status=status.HTTP_200_OK)
