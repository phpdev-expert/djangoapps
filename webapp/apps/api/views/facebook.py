import logging
from datetime import datetime, timedelta

import pandas as pd
import ast
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from webapp.apps.api.serializers.metrics import FacebookPageSerializer, MetricsAnalyticsPostSerializer, \
    FacebookPageVideoSerializer, PagePostSerializer
from webapp.apps.metrics.models import Page, Post, PageMetricsLifetime, PageMetricsDaily, Video, FACEBOOK
from webapp.base.base_api import BaseAPIView
from webapp.base.constants import POST_METRIC_FORMAT
from webapp.base.utils import generate_metric_value
from webapp.base.viewset_mixins import CreateViewSetMixin, CommonPostTableViewSetMixin

log = logging.getLogger('webapp')


class FacebookPageViewSet(BaseAPIView, ModelViewSet):
    queryset = Page.objects.prefetch_related().filter(
        type="facebook"
    ).order_by('-date_created')
    serializer_class = FacebookPageSerializer

    http_method_names = ['get']
    permission_classes = [AllowAny]


class FacebookPagePostViewSet(BaseAPIView, CreateViewSetMixin):
    queryset = Post.objects.filter(
        page__type=FACEBOOK
    ).order_by('-date_created')
    serializer_class = PagePostSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request_data = serializer.data

        posts = self.get_queryset().filter(
            page__page_id__in=request_data.get('page_urn')
        )
        if "start" in request_data:
            posts = posts.filter(post_date__date__gte=request_data.get('start'))
        if "end" in request_data:
            posts = posts.filter(post_date__date__lte=request_data.get('end'))

        #posts = posts.distinct("post_id")
        output = []
        for post in posts:
            tmp = {
                "urn": post.post_id,
                "name": post.title,
                "text": "",
                "post_date": post.post_date,
            }
            output.append(tmp)

        return Response(output)


class FacebookPagePostTableViewSet(CommonPostTableViewSetMixin):
    def get_queryset(self):
        return super().get_queryset().filter(
            page__type=FACEBOOK
        ).order_by('-date_created')


class FacebookPageAnalyticsViewSet(BaseAPIView, ModelViewSet):
    queryset = PageMetricsLifetime.objects.prefetch_related().filter(
        page__type="facebook"
    ).order_by('-date_created')
    serializer_class = MetricsAnalyticsPostSerializer

    http_method_names = ['post']
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        output = []

        # "shareCount":0,
        #       "clickCount":0,
        #       "engagement":0.0,
        #       "likeCount":0,
        #       "impressionCount":0,
        #       "commentCount":0,
        #       "date":"2019-04-30",
        #       "postCount":0

        metrics_format = {
            "page_total_actions": "clickCount",
            "page_post_engagements": "engagement",
            #"post_reactions_like_total": "likeCount",
            "page_impressions": "impressionCount",
            "post_impressions": "postCount",
            #"share_count":"shareCount",
            #"page_positive_feedback_by_type":"feedbackCount"
        }
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data

        start_time = data.get("start", None)
        end_time = data.get("end", None)

        if start_time == end_time and start_time is not None:
            end_time = datetime.strftime(
                datetime.strptime(end_time, "%Y-%m-%d") + timedelta(days=1),
                "%Y-%m-%d"
            )

        # page = Page.objects.filter(page_id__in=data["page_urn"])
        # if not page:
        #     raise Exception("Invalid page_urn")
        # else:
        #     page = page.first()

        params = {
            "page__page_id__in": data["page_urn"],
            #"page__type": page.type,
            "metrics__metric__in": [*metrics_format.keys(), "page_positive_feedback_by_type"],
        }
        if start_time:
            params["end_time__gte"] = start_time

        if end_time:
            params["end_time__lte"] = end_time

        output = []
        queryset = PageMetricsDaily.objects.filter(**params).order_by("end_time")
        records = []
        for item in queryset:
            date = datetime.strftime(item.end_time, "%Y-%m-%d")
            page_name = item.page.name
            value = item.value
            metric = item.metrics.metric
            if metric == "page_positive_feedback_by_type":
                # print(item.page.name, item.metrics.metric, item.value)
                # print("val", value)
                value = ast.literal_eval(value)
                records.append({"metric": "likeCount","date": date,"value": value["like"],"page": page_name})
                records.append({"metric": "commentCount","date": date,"value": value["comment"],"page": page_name})
                records.append({"metric": "shareCount","date": date,"value": value["link"],"page": page_name})
                

            else:
                metric = metrics_format.get(item.metrics.metric, False)
                if not metric:
                    continue
                value = int(item.value) if item.value_type in ["int", "float"] else 0
                records.append({
                    "metric": metric,
                    "date": date,
                    "value": value,
                    "page": page_name
                })

        metrics = metrics_format.values()
        metrics_values = {}
        for m in metrics:
            metrics_values[m] = 0

        if records:
            df = pd.DataFrame(records)
            # output = [{"name":name, "analytic":(data.pivot(index="date",columns="metric",values="value")).reset_index().to_dict(orient="records")}
            #           for name, data in df.groupby("page")]

            for name, data in df.groupby("page"):
                analytic = (data.pivot(index="date", columns="metric", values="value"))
                analytic = analytic.assign(**{k: metrics_values[k] for k in metrics if k not in analytic})
                analytic = analytic.fillna(0).reset_index().to_dict(orient="records")
                tmp = {
                    "name": name,
                    "analytic": analytic
                }
                output.append(tmp)

        # output = PageMetricsDailySerializer(queryset, many=True).data
        return Response(output, 200)
        # return super().list(request, *args, **kwargs)


class FacebookPageVideosViewSet(BaseAPIView, CreateViewSetMixin):
    queryset = Video.objects.all()
    serializer_class = FacebookPageVideoSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return super().get_queryset().filter(page__type=FACEBOOK).select_related('page')

    def create(self, request, *args, **kwargs):
        output = []

        metrics_format = {
            "page_video_views": "videoViews",
        }
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data

        start_time = data.get("start", None)
        end_time = data.get("end", None)

        if start_time == end_time and start_time is not None:
            end_time = datetime.strftime(
                datetime.strptime(end_time, "%Y-%m-%d") + timedelta(days=1),
                "%Y-%m-%d"
            )

        page = Page.objects.filter(page_id__in=data["page_urn"])
        if not page:
            raise Exception("Invalid page_urn")
        else:
            page = page.first()

        params = {
            "page__type": page.type,
            "metrics__metric__in": metrics_format.keys(),
        }
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
            # output = [{"name":name, "analytic":(data.pivot(index="date",columns="metric",values="value")).reset_index().to_dict(orient="records")}
            #           for name, data in df.groupby("page")]

            for name, data in df.groupby("page"):
                analytic = (data.pivot(index="date", columns="metric", values="value"))
                analytic = analytic.assign(**{k: metrics_values[k] for k in metrics if k not in analytic})
                analytic = analytic.fillna(0).reset_index().to_dict(orient="records")
                output.append(analytic)

        return Response(output)
        # return super().create(request, *args, **kwargs)