from itertools import chain
import numpy as np
from django.conf import settings

from rest_framework import status
from django.db.models.expressions import RawSQL
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import django_filters
from django.db.models import F, Count, Q
from rest_framework.decorators import api_view
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

import socket

from webapp.apps.metrics.analytics.twitter import TwitterAnalytics
from webapp.base.base_api import BaseAPIView
from webapp.apps.reports.models import WidgetTemplate
from webapp.apps.metrics.models import (
    Account,
    Metrics,
    MetricsAttribute,
    AccountMetrics,
    AccountObject,
    AccountInbox,
    TwitterMention,
    PostComments,
    CommentReplies,
)
from webapp.apps.api.serializers.metrics import (
    MetricsGetSerializer,
    MetricPostFilterSerializer,
)
from webapp.apps.api.cache import Cacher
from webapp.apps.api.serializers.accounts import AccountObjectSerializer
from webapp.apps.metrics.analytics import MetricComputation as MetricAnalyticComputation
from webapp.apps.metrics.analytics.facebook import FacebookMetricComputation
from webapp.apps.metrics.analytics.instagram import InstagramMetricComputation

from datetime import datetime, timedelta
import logging
import ast
import time


hostname = socket.gethostname()
if "Ashish" in hostname:
    pass
    # import query_debugger  # noqa

log = logging.getLogger("metric")

CUSTOM_METRICS = {
    "pageComment": {"type": "kv", "slug": "pageEngagementByType", "key": "comment"},
    "messageCount": {},
    "messages": {},
    "postTable": {},
    "postCount": {},  # linkedin, fb
    "receivedDm": {},  # twitter
    "inboundMessageTable": {},  # twitter
    "inboundMessage": {},  # twitter
    "postLikes": {},
    "postRetweet": {},
    "postReply": {},
    # "pageEngagement": {},
    "tweetTable": {},
    "pageTweet": {},
    "pageMention": {},
}
@api_view(["POST"])
def cleanup(request):
    message = []
    try:
        Metrics.objects.get(slug='postUniqueVideoViews').delete()
        message.append('removed postUniqueVideoViews')
    except Exception as e:
        message.append('failed to remove postUniqueVideoViews '+str(e))
    try:
        Metrics.objects.get(slug='postVideoViewsPaid').delete()
        message.append('removed postVideoViewsPaid')
    except Exception as e:
        message.append('failed to remove postVideoViewsPaid '+str(e))
    try:
        MetricsAttribute.objects.filter(metrics__platform='facebook',
                                metrics__slug = 'pageVideos30SecViews',
                                breakdown__in = ['organic','paid','auto', 'manual', 'repeat', 'unique']).delete()
        message.append('Removed pageVideos30SecViews attributes')
    except Exception as e:
        message.append('Failed to removed pageVideos30SecViews attributes '+ str(e))
    try:
        MetricsAttribute.objects.filter(metrics__platform='facebook',
                                metrics__slug = 'pageImpression',
                                breakdown__in = ['organic','paid','auto', 'manual', 'repeat', 'unique']).delete()
        message.append('Removed pageImpression attributes')
    except Exception as e:
        message.append('Failed to removed pageImpression attributes '+ str(e))
    try:
        MetricsAttribute.objects.filter(metrics__platform='facebook',
                                metrics__slug = 'pageVideos30SecViews',
                                breakdown__in = ['organic','paid','auto', 'manual', 'repeat', 'unique']).delete()
        message.append('Removed pageVideos30SecViews attributes')
    except Exception as e:
        message.append('Failed to removed pageVideos30SecViews attributes '+ str(e))
    try:
        MetricsAttribute.objects.filter(metrics__platform='facebook',
                                metrics__slug = 'pageVideosViews',
                                breakdown__in = ['organic','paid','auto', 'manual', 'repeat', 'unique']).delete()
        message.append('Removed pageVideosViews attributes')
    except Exception as e:
        message.append('Failed to removed pageVideosViews attributes '+ str(e))
    try:
        WidgetTemplate.objects.get(id=73).delete()
        message.append('Removed widgettemplate with id 73')
    except Exception as e:
        message.append('Failed to remove widgettemplate with id 73 '+ str(e))
    try:
        WidgetTemplate.objects.get(id=77).delete()
        message.append('Removed widgettemplate with id 77')
    except Exception as e:
        message.append('Failed to remove widgettemplate with id 77 '+ str(e))

    return Response({"details":message}, status=status.HTTP_200_OK)

class MetricComputation:
    @staticmethod
    def extract_sub_metrics(
        page_id, metric, values, date, account_metrics_mapping, name
    ):
        if metric == "page_positive_feedback_by_type":
            value = values["like"]
            slug = "likeCount"

            if slug not in account_metrics_mapping:
                account_metrics_mapping[page_id] = []

            account_metrics_mapping[page_id].append(
                {"value": value, "date": date, "slug": metric, "name": name}
            )
        return account_metrics_mapping

    @staticmethod
    def get_metrics_mapping(account_metrics):
        account_metrics_mapping = {}
        for m in account_metrics:
            if m.account.page_id not in account_metrics_mapping:
                account_metrics_mapping[m.account.page_id] = []

            metric = m.metrics.slug
            name = m.metrics.name
            page_id = m.account.page_id
            date = m.date
            if metric == "page_positive_feedback_by_type":
                value = ast.literal_eval(m.value)
                account_metrics_mapping = MetricComputation.extract_sub_metrics(
                    page_id, metric, value, date, account_metrics_mapping, name
                )
                continue

            # if metric not in account_metrics_mapping:
            #     account_metrics_mapping[m.account.page_id][metric] = []

            account_metrics_mapping[page_id].append(
                {"value": m.value, "date": date, "slug": metric, "name": name}
            )

        return account_metrics_mapping

    @staticmethod
    def filter_lifetime(account_metrics, data):
        params = {}
        if "since" in data:
            params["date__gte"] = data["since"]
        if "until" in data:
            params["date__lte"] = datetime.strptime(
                data["until"], "%Y-%m-%d"
            ) + timedelta(days=1)
        if not params:
            return account_metrics

        lifetime_metrics = account_metrics.filter(metrics__fields__period="lifetime")
        non_lifetime = account_metrics.exclude(
            id__in=lifetime_metrics.values("id")
        ).filter(**params)
        return lifetime_metrics | non_lifetime

    @staticmethod
    def get_date_params(input_params, date_field):
        params = {}
        if "since" in input_params:
            params[f"{date_field}__gte"] = input_params["since"]
        if "until" in input_params:
            params[f"{date_field}__lte"] = datetime.strptime(
                input_params["until"], "%Y-%m-%d"
            ) + timedelta(days=1)
        return params

    @staticmethod
    def get_all_pages(auth_user, platform):
        accounts = list(
            Account.objects.filter(user_id=auth_user, type__in=platform, status__in=["active", "revoked"]).values_list(
                "page_id", flat=True
            )
        )
        return accounts

    @staticmethod
    def get_custom_slug_metrics(
        custom_slugs,
        auth_user,
        page_ids,
        input_params,
        agg_post=False,
        rules={"breakdown": None, "agg": "As is"},
    ):
        account_metrics_mapping = {}
        log.info("custom slugs : {}".format(custom_slugs))
        ao_date_params = MetricComputation.get_date_params(input_params, "date_posted")
        date_params = MetricComputation.get_date_params(input_params, "date")

        for c in custom_slugs:
            if c == "pageMention":
                mentions = (
                    TwitterMention.objects.filter(
                        account__user_id=auth_user,
                        account__page_id__in=page_ids,
                        **date_params,
                    )
                    .values("account__page_id")
                    .annotate(count=Count("account__page_id"))
                )
                TwitterAnalytics.compute_pageMention(
                    mentions, rules, c, account_metrics_mapping
                )
            if c == "postEngagement":
                posts = AccountObject.objects.filter(
                    account__user_id=auth_user,
                    account__page_id__in=page_ids,
                    **ao_date_params,
                ).values_list("object_id", flat=True)

                metrics = AccountMetrics.objects.filter(
                    account__user_id=auth_user,
                    account__page_id__in=page_ids,
                    object_id__object_id__in=posts,
                    metrics__slug__in=["postReactions", "postShares","postComments"],
                )
                date_idx = {}
                output = []
                for metric in metrics:
                    if metric.date in date_idx:
                        idx = date_idx[metric.date]
                        if metric.metrics.name in output[idx]["value"]:
                            output[idx]["value"][metric.metrics.name] += int(metric.value)
                        else:
                            output[idx]["value"][metric.metrics.name] = int(metric.value)
                    else:
                        output.append({
                            "value":{metric.metrics.name: int(metric.value)},
                            "date":metric.date,
                            "slug":c,
                            "name":c
                        })
                        date_idx.update({metric.date: len(output)-1})
                account_metrics_mapping = output
                return account_metrics_mapping

            if c == "pageEngagement":
                # for page_id in page_ids:
                #     count = 0
                posts = AccountObject.objects.filter(
                    account__user_id=auth_user,
                    account__page_id__in=page_ids,
                    **ao_date_params,
                ).values_list("object_id", flat=True)

                reply = (
                    AccountObject.objects.filter(
                        account__user_id=auth_user,
                        account__page_id__in=page_ids,
                        object_id__in=posts,
                        **ao_date_params,
                    )
                    .values("account__page_id")
                    .annotate(reply=Count("twitterreply"))
                )

                metrics = AccountMetrics.objects.filter(
                    account__user_id=auth_user,
                    account__page_id__in=page_ids,
                    object_id__object_id__in=posts,
                    metrics__slug__in=["postLikes", "postRetweet"],
                    # **date_params,
                )
                TwitterAnalytics.compute_pageEngagement(
                    metrics, reply, rules, c, account_metrics_mapping
                )

            if c == "postLikes" or c == "postRetweet":
                posts = AccountObject.objects.filter(
                    account__user_id=auth_user,
                    account__page_id__in=page_ids,
                    **ao_date_params,
                ).values_list("object_id", flat=True)

                metrics = AccountMetrics.objects.filter(
                    account__user_id=auth_user,
                    account__page_id__in=page_ids,
                    object_id__object_id__in=posts,
                    metrics__slug=c,
                )
                TwitterAnalytics.compute_postLikes_postRetweet(
                    metrics, rules, c, agg_post, account_metrics_mapping
                )

            if c == "postReply":
                posts = (
                    AccountObject.objects.filter(
                        account__user_id=auth_user,
                        account__page_id__in=page_ids,
                        **ao_date_params,
                    )
                    .values("account__page_id", "date_posted", "title", "object_id")
                    .annotate(reply=Count("twitterreply"))
                )
                TwitterAnalytics.compute_postReply(
                    posts, rules, c, agg_post, account_metrics_mapping
                )

            if c == "inboundMessage":
                inbox_params = MetricComputation.get_date_params(
                    input_params, "accountinbox__date"
                )
                mention_params = MetricComputation.get_date_params(
                    input_params, "twittermention__date"
                )

                inbound_table = (
                    Account.objects.filter(
                        user_id=auth_user,
                        page_id__in=page_ids,
                        # **date_params,
                    )
                    .values("page_id")
                    .annotate(
                        inbox=Count(
                            "accountinbox", distinct=True, filter=Q(**inbox_params)
                        ),
                        mention=Count(
                            "twittermention", distinct=True, filter=Q(**mention_params)
                        ),
                    )
                )
                account_metrics_mapping = TwitterAnalytics.compute_inboundMessage(
                    inbound_table, account_metrics_mapping, rules, c
                )

            if c == "inboundMessageTable":

                inbound_table = chain.from_iterable(
                    [
                        AccountInbox.objects.filter(
                            account__user_id=auth_user,
                            account__page_id__in=page_ids,
                            **date_params,
                        ),
                        TwitterMention.objects.filter(
                            account__user_id=auth_user,
                            account__page_id__in=page_ids,
                            **date_params,
                        ),
                    ]
                )
                account_metrics_mapping = TwitterAnalytics.compute_inboundMessageTable(
                    inbound_table, account_metrics_mapping, rules, c
                )

            if c == "postCount" or c == "pageTweet":
                posts_count = (
                    AccountObject.objects.filter(
                        account__user_id=auth_user,
                        account__page_id__in=page_ids,
                        **ao_date_params,
                    )
                    .values("account__page_id")
                    .annotate(count=Count("account__page_id"))
                )
                posts_count = {
                    item["account__page_id"]: item["count"] for item in posts_count
                }
                for page_id in page_ids:
                    metric = {
                        "value": posts_count.get(str(page_id), 0),
                        "date": "",
                        "slug": c,
                        "name": c,
                    }
                    account_metrics_mapping.setdefault(str(page_id), []).append(metric)

            if c == "messageCount" or c == "receivedDm":
                inbox_params = MetricComputation.get_date_params(
                    input_params, "accountinbox__date"
                )
                account_object_params = MetricComputation.get_date_params(
                    input_params, "accountobject__date_posted"
                )
                messages_count = (
                    Account.objects.filter(user_id=auth_user, page_id__in=page_ids)
                    .values("page_id")
                    .annotate(inbox=Count("accountinbox", filter=Q(**inbox_params)))
                )
                messages_comments_count = {
                    item["page_id"]: int(item["inbox"]) for item in messages_count
                }
                if c == "messageCount":
                    comments_count = (AccountObject.objects.filter(
                        account__user_id=auth_user,
                        account__page_id__in=page_ids,
                        **ao_date_params).select_related()
                                      ).values("account__page_id", "data__comment_count")
                    for pagecomment in comments_count:
                        if pagecomment["account__page_id"] in messages_comments_count:
                            messages_comments_count[pagecomment["account__page_id"]] += int(pagecomment["data__comment_count"])
                        else:
                            messages_comments_count[pagecomment["account__page_id"]] = int(pagecomment["data__comment_count"])
                for page_id in page_ids:
                    metric = {
                        "value": messages_comments_count.get(str(page_id), 0),
                        "date": "",
                        "slug": c,
                        "name": c,
                    }
                    account_metrics_mapping.setdefault(str(page_id), []).append(metric)

            elif c == "messages":
                for page_id in page_ids:
                    messages = list(
                        AccountInbox.objects.filter(
                            account__user_id=auth_user,
                            account__page_id=page_id,
                            **date_params,
                        ).values("author", "message", "date")
                    )
                    post_date_params = MetricComputation.get_date_params(
                        input_params, "date_posted"
                    )
                    posts = AccountObject.objects.select_related("account").filter(
                        account__user_id=auth_user,
                        account__page_id=page_id,
                        object_type="post",
                        **post_date_params,
                    )
                    comments = PostComments.objects.filter(object__in=posts)
                    messages += list(comments.values("author", "message", "date"))
                    messages += list(
                        CommentReplies.objects.filter(comment__in=comments).values(
                            "author", "message", "date"
                        )
                    )

                    metric = {"value": messages, "date": "", "slug": c, "name": c}
                    account_metrics_mapping.setdefault(page_id, []).append(metric)

            elif c == "postTable" or c == "tweetTable":
                queryset = AccountObject.objects.filter(
                    account__user_id=auth_user,
                    account__page_id__in=page_ids,
                    object_type="post",
                    **ao_date_params,
                ).order_by("-date_posted")
                objects = AccountObjectSerializer(queryset, many=True).data
                for o in objects:
                    metric = {"value": o, "date": "", "slug": c, "name": c}
                    account_metrics_mapping.setdefault(o["page_id"], []).append(metric)
        if (rules["breakdown"] not in ["page", "post"]):
            account_metrics_mapping = MetricAnalyticComputation.get_sum_across_page(
                account_metrics_mapping
            )
        return account_metrics_mapping

    @staticmethod
    def get_slugs(names, data, has_slugs=False):

        if "," in names:
            _names = names.split(",")
            names = []
            for s in _names:
                names.append(s.strip())
        else:
            names = [names]

        slugs = []
        attributes = dict()
        agg_post = False
        post_name = "post" if has_slugs else "Post "
        metric_filter = "metrics__slug__in" if has_slugs else "metrics__name__in"
        post_len = 4 if has_slugs else 5

        try:
            params = {"metrics__platform__in": data["platform"], metric_filter: names}
            agg_post = post_name == params[metric_filter][0][0:post_len]
            if not agg_post:
                if "object_id" not in data:
                    params["breakdown"] = data["breakdown"].lower()

            log.info("metric attributes params : {}".format(params))
            slugs = []

            maa = MetricsAttribute.objects.select_related("metrics").filter(**params)
            log.info("metric attributes :: {}".format(maa))
            for m in maa:
                slug = m.metrics.slug
                if m.ref_metric:
                    slug = m.ref_metric.slug
                slugs.append(slug)

            slugs = [*{*slugs}]

            attributes = list(
                Metrics.objects.filter(platform__in=data["platform"], name__in=names)
                .annotate(
                    breakdown=F("metricsattribute__breakdown"),
                    aggregration=F("metricsattribute__aggregration"),
                )
                .values("breakdown", "aggregration").distinct()
            )
        except Exception as ex:
            print("ex,", ex)

        log.info("final slugs : {}".format(slugs))
        log.info("agg post : {}".format(agg_post))
        filter_slugs = []
        custom_slugs = []
        for s in slugs:
            if s in CUSTOM_METRICS.keys() or (
                "twitter" in data["platform"] and s == "pageEngagement"
            ) or ("linkedin" in data["platform"] and s == "postEngagement" and data["breakdown"]== "type"):
                custom_slugs.append(s)
            else:
               filter_slugs.append(s)

        return filter_slugs, custom_slugs, agg_post, attributes

    @staticmethod
    def get_metrics(slug_params, data, auth_user, page_ids):
        page_ids = list(page_ids)
        output = []
        CACHE_KEY = False
        page_ids.sort()
        if settings.CACHE_METRICS:
            try:
                slug_keys = (
                    "_".join(slug_params[0])
                    + "_"
                    + "_".join(slug_params[1])
                    + "_"
                    + str(slug_params[2])
                )
                CACHE_KEY = "metrics_{}_{}_{}_{}_{}_{}".format(
                    auth_user,
                    slug_keys,
                    data["breakdown"],
                    "_".join(page_ids),
                    data.get("since", ""),
                    data.get("until", ""),
                )
                output = Cacher.get(CACHE_KEY)
            except Exception:
                pass
        if not output:
            output = []
            filter_slugs, custom_slugs, agg_post = slug_params
            if agg_post and data["breakdown"] != "post":
                data["aggregration"] = "post"
            metrics_names = {}
            all_slugs = filter_slugs + custom_slugs
            for m in Metrics.objects.filter(slug__in=all_slugs):
                metrics_names[m.slug] = m.name
            a2 = {}
            if data["breakdown"] not in ["page", "post"]:
                a2 = []

            if "instagram" in data["platform"]:  # and data["aggregration"] != "As is":
                accounts = Account.objects.filter(
                    user_id=auth_user, page_id__in=page_ids
                )
                account_metrics_mapping = InstagramMetricComputation().get_metrics_mapping(
                    filter_slugs + custom_slugs, data, accounts
                )
                data["platform"] = [p for p in data["platform"] if p != "instagram"]

            if data["platform"]:

                params = {
                    "account__user_id": str(auth_user),
                    "metrics__platform__in": data["platform"],
                    "metrics__slug__in": filter_slugs,
                    "object_id": None,
                    "account__page_id__in": page_ids,
                }

                if agg_post:
                    ao_params = {
                        **MetricComputation.get_date_params(data, "date_posted"),
                        "account__user_id": auth_user,
                        "account__page_id__in": page_ids,
                    }

                    ao = AccountObject.objects.filter(**ao_params)
                    if not ao:
                        return []
                    params["object_id_id__in"] = list(ao.values_list("id", flat=True))
                    params.pop("object_id")

                else:
                    if "object_id" in data:
                        ao = AccountObject.objects.filter(
                            object_id=data["object_id"], account__user_id=auth_user
                        )
                        if not ao:
                            return []
                        params["object_id_id__in"] = list(
                            ao.values_list("id", flat=True)
                        )
                        params.pop("object_id")

                rules = {"breakdown": data["breakdown"], "agg": data["aggregration"]}

                log.info("metric params : {}".format(params))
                account_metrics = AccountMetrics.objects.select_related(
                    "metrics", "account"
                ).filter(**params)
                if not ("linkedin" in data["platform"] and agg_post):
                    account_metrics = MetricComputation.filter_lifetime(
                        account_metrics, data
                    ).all()
                # print(account_metrics.first().value)
                log.info("metric queryset : {}".format(account_metrics.count()))
                account_metrics_mapping = FacebookMetricComputation().get_metrics_mapping(
                    account_metrics, rules, agg_post
                )
                a2 = MetricComputation.get_custom_slug_metrics(
                    custom_slugs, auth_user, page_ids, data, agg_post, rules
                )


            if type(account_metrics_mapping) == dict and type(a2) == dict:

                account_metrics_mapping = {**account_metrics_mapping, **a2}
                log.info("metric output : {}".format(account_metrics_mapping.keys()))

                _pages = list(
                    Account.objects.filter(
                        page_id__in=list(account_metrics_mapping.keys()),
                        user_id=auth_user,
                    )
                    .annotate(
                        profile_pic_url=RawSQL("data->>'profile_pic_url'", params=())
                    )
                    .values("page_id", "name", "type", "profile_pic_url")
                )
                pages = {}
                page_data = {}
                for p in _pages:
                    pages.update({p["page_id"]: p["name"]})
                    page_data.update({p["page_id"]: p})

            if data["breakdown"] not in ["page", "post"]:
                if all([account_metrics_mapping, a2]):
                    output = account_metrics_mapping + a2
                elif account_metrics_mapping:
                    output = account_metrics_mapping
                elif a2:
                    output = a2

            elif agg_post and data["aggregration"] == "post" and data["breakdown"]:
                for page_id, metrics in account_metrics_mapping.items():
                    for m in metrics:
                        tmp = {
                            "value": m["value"],
                            "date": data["since"] + " - " + data["until"]
                            if "since" in data and "until" in data
                            else m["date"],
                            "slug": m["slug"],
                            "name": metrics_names.get(m["slug"], ""),
                            "page": {"id": page_id, "name": pages.get(page_id)},
                        }

                        value = _v = m["value"]
                        try:
                            if type(value) == dict:
                                _v = 0
                                for k1, v1 in value.items():
                                    _v += int(v1)
                                value = int(_v)
                            else:
                                value = int(value)
                        except Exception:
                            value = 0

                        found = False
                        for index, item in enumerate(output):
                            if (
                                tmp["slug"] == item["slug"]
                                and tmp["page"] == item["page"]
                            ):
                                output[index]["value"] += value
                                found = True
                                break
                        if not found:
                            tmp["value"] = value
                            output.append(tmp)

            else:
                for page_id, metrics in account_metrics_mapping.items():
                    page_id = str(page_id)
                    page = {
                        "id": page_id,
                        "name": pages.get(page_id),
                        "platform": page_data.get(page_id)["type"],
                        "profile_pic_url": page_data.get(page_id).get(
                            "profile_pic_url", None
                        ),
                    }
                    for m in metrics:
                        value = m["value"]
                        if type(value) == np.int64:
                            value = int(value)

                        tmp = {
                            "value": value,
                            "date": m["date"],
                            "slug": m["slug"],
                            "name": metrics_names.get(m["slug"], ""),
                            "page": page,
                        }
                        tmp.update(**m.get("data", {}))
                        output.append(tmp)

            if data["breakdown"] == "post":
                if len(output) > 0:
                    if "post_id" in output[0]:
                        # aggregrate by post id
                        _final = {}
                        for row in output:
                            post_id = row["post_id"]
                            if post_id not in _final:
                                _final[post_id] = {
                                    "page": row["page"],
                                    "post_id": post_id,
                                    "title": row["title"],
                                    "date": row["date"],
                                    "social": {},
                                    **row.get("data", {}),
                                }

                            _final[post_id]["social"][row["name"]] = row["value"]

                        output = list(_final.values())

            if CACHE_KEY:
                Cacher.set(CACHE_KEY, output)
        return output


class MetricsViewSet(BaseAPIView, ModelViewSet, FacebookMetricComputation):
    queryset = Metrics.objects.prefetch_related().filter().order_by("-date_created")
    serializer_class = MetricsGetSerializer
    http_method_names = ["get", "post"]
    permission_classes = [AllowAny]
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filter_fields = ("platform",)
    lookup_field = "name"

    def get_serializer(self, *args, **kwargs):

        serializer_class = self.get_serializer_class()
        if self.request.method == "POST":
            serializer_class = MetricPostFilterSerializer
        return serializer_class(*args, **kwargs)

    @swagger_auto_schema(
        manual_parameters=[
            # openapi.Parameter("pageid", openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter("level", openapi.IN_QUERY, type=openapi.TYPE_STRING)
        ]
    )
    def list(self, request, *args, **kwargs):
        level = request.GET.get("level")
        platform = request.GET.get("platform")
        params = dict()
        if level:
            if platform == "linkedin" and level == "post":
                params.update({"fields__is_post": True})

            elif platform == "instagram" and level == "post":
                # for instagtram get only count metrics for post
                params.update(
                    {"fields__level__icontains": level, "metric__icontains": "count"}
                )
            else:
                params.update({"fields__level__icontains": level})
        queryset = Metrics.objects.prefetch_related().filter(
            platform=platform, **params
        )
        # metrics = MetricsGetSerializer(queryset, many=True).data
        metrics = []
        um = {}

        for q in queryset:
            # add metrics and its attributes to dict
            if q.name not in um:
                um[q.name] = {
                    "name": q.name,
                    "slug": q.slug,
                    "description": q.description,
                    "platform": q.platform,
                    "attributes": list(
                        q.metricsattribute_set.values(
                            "breakdown", "aggregration"
                        ).distinct()
                    ),
                }
            # update attributes of metrics already present in the dict
            elif q.metricsattribute_set.values("breakdown", "aggregration"):
                um[q.name]["attributes"] = list(
                    q.metricsattribute_set.values(
                        "breakdown", "aggregration"
                    ).distinct()
                )

        for k, v in um.items():
            metrics.append(v)

        return Response(metrics, 200)

    # @swagger_auto_schema(
    #     manual_parameters=[
    #         openapi.Parameter("pageid", openapi.IN_BODY, type=openapi.TYPE_STRING),
    #         openapi.Parameter("platform", openapi.IN_BODY, type=openapi.TYPE_STRING),
    #         openapi.Parameter("object_id", openapi.IN_BODY, type=openapi.TYPE_STRING),
    #         openapi.Parameter("breakdown", openapi.IN_BODY, type=openapi.TYPE_STRING),
    #         openapi.Parameter(
    #             "aggregration", openapi.IN_BODY, type=openapi.TYPE_STRING
    #         ),
    #         openapi.Parameter("since", openapi.IN_BODY, type=openapi.FORMAT_DATE),
    #         openapi.Parameter("until", openapi.IN_BODY, type=openapi.FORMAT_DATE),
    #         openapi.Parameter("slug", openapi.IN_QUERY, type=openapi.TYPE_STRING),
    #     ]
    # )

    def create(self, request, *args, **kwargs):
        start_time = time.time()
        output = []
        auth_user = request.auth_user_id
        serializer = MetricPostFilterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        page_ids = request.page_ids
        if not page_ids:
            page_ids = data.get("pageid", [])
            if page_ids:
                page_ids = page_ids.split(",")

        data["platform"] = data["platform"].split(",")

        if not page_ids:
            page_ids = MetricComputation.get_all_pages(auth_user, data["platform"])

        log.info("names input : {}".format(data["name"]))
        log.info("slug input : {}".format(data.get("slug", "")))
        if "slug" in data:
            (
                filter_slugs,
                custom_slugs,
                agg_post,
                attributes,
            ) = MetricComputation.get_slugs(data["slug"], data, True)
        else:
            (
                filter_slugs,
                custom_slugs,
                agg_post,
                attributes,
            ) = MetricComputation.get_slugs(data["name"], data)
        output = MetricComputation.get_metrics(
            (filter_slugs, custom_slugs, agg_post), data, auth_user, page_ids
        )
        log.info("--- %s seconds ---" % (time.time() - start_time))
        log.info("output size : {}".format(len(output)))
        if not output:
            return Response([], 200)
        return Response(output, 200)