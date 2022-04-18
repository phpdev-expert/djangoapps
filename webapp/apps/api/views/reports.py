from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from webapp.base.base_api import BaseAPIView
from webapp.apps.metrics.models import Account, AccountMetrics
from webapp.apps.reports.models import Reports, UserReportMapping, Widget
from webapp.apps.api.serializers.reports import (
    ReportSerializer,
    ReportGetRequestSerializer,
    WidgetSerializer,
    WidgetPostListSerializer,
    ReportWidgetSerializer,
)
import ast
import logging

log = logging.getLogger("webapp")


class MetricComputation:
    def extract_sub_metrics(
        self, page_id, metric, values, date, account_metrics_mapping
    ):
        if metric == "page_positive_feedback_by_type":
            value = values["like"]
            slug = "likeCount"

            if slug not in account_metrics_mapping:
                account_metrics_mapping[page_id] = []

            account_metrics_mapping[page_id].append(
                {"value": value, "date": date, "slug": metric}
            )
        return account_metrics_mapping

    def get_metrics_mapping(self, account_metrics):
        account_metrics_mapping = {}
        for m in account_metrics:
            if m.account.page_id not in account_metrics_mapping:
                account_metrics_mapping[m.account.page_id] = []

            metric = m.metrics.slug
            page_id = m.account.page_id
            date = m.date
            if metric == "page_positive_feedback_by_type":
                value = ast.literal_eval(m.value)
                account_metrics_mapping = self.extract_sub_metrics(
                    page_id, metric, value, date, account_metrics_mapping
                )
                continue

            # if metric not in account_metrics_mapping:
            #     account_metrics_mapping[m.account.page_id][metric] = []

            account_metrics_mapping[page_id].append(
                {"value": m.value, "date": date, "slug": metric}
            )

        return account_metrics_mapping


class ReportsViewSet(BaseAPIView, ModelViewSet, MetricComputation):
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

    def prepare_widgets(self, report, account_metrics_mapping):
        widgets = {}
        page_ids = list(account_metrics_mapping.keys())
        _pages = list(
            Account.objects.filter(page_id__in=page_ids).values(
                "page_id", "name", "type"
            )
        )
        pages = {p["page_id"]: p["name"] for p in _pages}
        # platform = {p["page_id"]: p["type"] for p in _pages}

        for w in report.widgets.all():
            widget_slug = w.type
            metric = []

            # get values from each page
            for p in page_ids:
                rr = account_metrics_mapping.get(p, {})
                for r in rr:
                    if r["slug"] == widget_slug:
                        # if w.style["type"] in ["pie", "list", "number"]:
                        value = 0

                        try:
                            value += int(r["value"])
                        except:  # noqa E722
                            pass
                        metric.append(
                            {
                                "value": value,
                                "date": r["date"],
                                "page": {"id": p, "name": pages[p]},
                            }
                        )

            widgets[w.id] = {
                "platform": w.report.platform,
                "type": w.type,
                "metric": metric,
                "style": w.style,
            }
        return widgets

    def prepare_report(self, page_ids, report, params):

        account_metrics = AccountMetrics.objects.filter(
            object_id=None,
            # account__type=report.platform,
            account__page_id__in=page_ids,
            account__user_id=self.request.auth_user_id,
        )
        if report.platform != "twitter":
            account_metrics = self._filter_queryset(account_metrics, params)
        account_metrics_mapping = self.get_metrics_mapping(account_metrics)
        widgets = self.prepare_widgets(report, account_metrics_mapping)
        report = {"report_id": report.id, "widgets": widgets}
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

        params = serializer.data
        output = self.prepare_report(request.page_ids, report, params)

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
        instance = self.get_object()
        instance.delete()
        return Response("Report Deleted", status=status.HTTP_204_NO_CONTENT)


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
        for widget in data["widgets"]:
            style = widget["style"]
            widget_id = widget.get("id", False)
            if widget_id:
                try:
                    w = Widget.objects.get(id=widget_id)
                except:  # noqa E722
                    pass
                else:
                    w.type = widget["type"]
                    w.style = style
                    w.save()
            else:
                Widget.objects.get_or_create(
                    report_id=kwargs["report_pk"],
                    type=widget["type"],
                    defaults={"style": style},
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
        return Response("Widget Deleted", status=status.HTTP_204_NO_CONTENT)
