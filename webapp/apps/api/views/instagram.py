import logging
from datetime import datetime, timedelta

import pandas as pd
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from webapp.apps.api.serializers.metrics import FacebookPageSerializer, MetricsAnalyticsPostSerializer
from webapp.apps.metrics.models import Page, Post, PageMetricsLifetime, PageMetricsDaily, INSTAGRAM
from webapp.base.base_api import BaseAPIView
from webapp.base.viewset_mixins import CommonPostTableViewSetMixin

log = logging.getLogger('webapp')


class InstagramPageViewSet(BaseAPIView, ModelViewSet):
    queryset = Page.objects.prefetch_related().filter(
        type="instagram"
    ).order_by('-date_created')
    serializer_class = FacebookPageSerializer

    http_method_names = ['get']
    permission_classes = [AllowAny]


class InstagramPagePostTableViewSet(CommonPostTableViewSetMixin):
    def get_queryset(self):
        return super().get_queryset().filter(
            page__type=INSTAGRAM
        ).order_by('-date_created')


class InstagramPageAnalyticsViewSet(BaseAPIView, ModelViewSet):
    queryset = PageMetricsLifetime.objects.prefetch_related().filter(
        page__type="instagram"
    ).order_by('-date_created')
    serializer_class = MetricsAnalyticsPostSerializer

    http_method_names = ['post']
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        output = []

        # output = [
        #     {
        #       "name": "Tata AIG",
        #       "analytic": [
        #         {
        #           "date": "2020-01-09",
        #           "engagement": 7121,
        #           "impressionCount": 295587,
        #           "clickCount": 0,
        #           "likeCount": 0,
        #           "postCount": 0,
        #           "shareCount": 0,
        #           "commentCount": 0
        #         },
        #       ]
        #     }
        #   ]

        metrics_format = {
            "impressions": "impressionCount",
            "email_contacts": "postCount",
            "reach": "engagement",
            "follower_count": "likeCount",
            #"post_impressions": "postCount",
            "phone_call_clicks": "shareCount",
            "phone_call_clicks": "commentCount"
        }

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data

        start_time = data.get("start", None)
        end_time = data.get("end", None)

        page = Page.objects.filter(page_id__in=data["page_urn"])
        if not page:
            raise Exception("Invalid page_urn")
        else:
            page = page.first()

        if start_time == end_time and start_time is not None:
            end_time = datetime.strftime(
                datetime.strptime(end_time, "%Y-%m-%d") + timedelta(days=1),
                "%Y-%m-%d"
            )

        params = {"metrics__metric__in": metrics_format.keys(),
                  "page__type": page.type}
        if start_time:
            params["end_time__gte"] = start_time

        if end_time:
            params["end_time__lte"] = end_time

        output = []
        queryset = PageMetricsDaily.objects.filter(**params).order_by("end_time")
        records = []
        for item in queryset:
            metric = metrics_format.get(item.metrics.metric, False)
            if not metric:
                continue

            value = int(item.value) if item.value_type in ["int", "float"] else 0
            records.append({
                "metric": metric,
                "date": datetime.strftime(item.end_time, "%Y-%m-%d"),
                "value": value,
                "page": item.page.name
            })

        metrics = metrics_format.values()
        metrics_values = {}
        for m in metrics:
            metrics_values[m] = 0

        if records:
            df = pd.DataFrame(records)
            for name, data in df.groupby("page"):
                analytic = (data.pivot(index="date", columns="metric", values="value"))
                analytic = analytic.assign(**{k: metrics_values[k] for k in metrics if k not in analytic})
                analytic = analytic.fillna(0).reset_index().to_dict(orient="records")
                tmp = {
                    "name": name,
                    "analytic": analytic
                }
                output.append(tmp)

        return Response(output, 200)
