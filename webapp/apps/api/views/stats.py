from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from django.db.models import Sum
from django.db.models.functions import Cast
from django.db.models import IntegerField, FloatField

from webapp.base.base_api import BaseAPIView
from webapp.apps.api.views.metrics_v2 import MetricComputation
from webapp.apps.api.serializers.metrics import MetricPostFilterSerializer
from webapp.apps.metrics.models import AccountMetrics, AccountObject, Metrics, Account
from webapp.apps.api.serializers.stats import StatsHealthSerializer
from webapp.apps.api.cache import Cacher

import logging

import pandas as pd
import ast

log = logging.getLogger("report")


def to_int(x):
    v = 0
    try:
        v = int(x)
    except Exception:
        pass
    return v


def _to_int(all_x):
    output = []
    for x in all_x:
        v = to_int(x)

        output.append(v)
    return output


def get_post_reactions(row, page_details):
    page_id = row["page_id"].values[0]
    platform = page_details[page_id]["platform"]
    count = 0
    if platform == "instagram":
        count = row.get("Fans", 0)
    else:
        # print(row)
        count = row.get("Post Reactions", 0)
    return count


def get_fans(row, page_details):
    page_id = row["page_id"].values[0]
    platform = page_details[page_id]["platform"]
    count = 0
    if platform == "facebook":
        count = row.get("Fans", 0)
    else:
        count = row.get("Followers", 0)
    return count


def get_post_likes(row, account_objects, page_details):
    count = 0
    page_id = row["page_id"].values[0]

    platform = page_details[page_id]["platform"]
    if platform == "instagram":
        posts = account_objects[account_objects["account__page_id"] == page_id]
        count = posts.data.apply(lambda x: to_int(x.get("like_count", 0))).sum()
        count = int(count)

    elif platform == "facebook":
        count = row.get("Post Reactions: Like", 0)
        if count == 0:
            count = row.get("_Post Likes", 0)
    elif platform == "twitter":
        count = row.get("Post Likes", 0)
    elif platform == "linkedin":
        count = row.get("Post Reactions", 0)
    return count


class StatHealthViewSet(BaseAPIView, ModelViewSet):
    queryset = Metrics.objects.filter().order_by("-date_created")
    serializer_class = StatsHealthSerializer

    http_method_names = ["get"]
    # lookup_field = "id"

    def list(self, request, *args, **kwargs):
        metricSlug = {
            "linkedin": ["postEngagement", "postCount", "pageFollower"],
            "facebook": ["pagePostEngagement", "postCount", "pageFans"],
            "twitter": ["pageEngagement", "pageFollower", "pageTweet"],
            "instagram": [
                "pagePosts",
                "pageFollowers",
                "pagePostComments",
                "postLikes",
            ],
        }
        CACHE_KEY = f"stat_health_{request.auth_user_id}"
        output = Cacher.get(CACHE_KEY)
        if not output:
            params = {
                "user_id": request.auth_user_id,
                "status__in": ["active", "revoked"],
            }
            output = []
            for page in Account.objects.exclude(
                data__contains={"account_type": "PERSONAL"}, type="instagram"
            ).filter(**params):
                row = {
                    "Page Engagement": 0,
                    "Page Fans": 0,
                    "Posts": 0,
                    "page_id": page.page_id,
                    "page_name": page.name,
                    "picture_url": page.data.get("profile_pic_url", "")
                    if page.data
                    else "",
                    "platform": page.type,
                }
                platform = page.type
                for slug in metricSlug[platform]:
                    if slug in ["postCount", "pagePosts", "pageTweet"]:
                        row["Posts"] = AccountObject.objects.filter(
                            account=page
                        ).count()
                    elif slug in [
                        "pageFollower",
                        "pageFans",
                        "pageTweet",
                        "pageFollowers",
                    ]:
                        m = Metrics.objects.get(slug=slug, platform=platform)
                        fans = (
                            AccountMetrics.objects.filter(account=page, metrics=m)
                            .values_list("value", flat=True)
                            .last()
                        )
                        if fans:
                            row["Page Fans"] = fans
                    elif slug in [
                        "postEngagement",
                        "pagePostEngagement",
                        "pageEngagement",
                        "pageFollowers",
                    ]:
                        m = Metrics.objects.get(slug=slug, platform=platform)
                        engagement = AccountMetrics.objects.filter(
                            account=page, metrics=m
                        ).aggregate(value=Sum(Cast("value", FloatField())))
                        if engagement["value"]:
                            row["Page Engagement"] = int(engagement["value"])
                    elif slug in ["pagePostComments", "postLikes"]:
                        posts = AccountObject.objects.filter(account=page)
                        engagement = 0
                        for p in posts:
                            engagement += int(p.data.get("comments_count", 0)) + int(
                                p.data.get("like_count", 0)
                            )
                        row["Page Engagement"] = engagement

                output.append(row)
            Cacher.set(CACHE_KEY, output)

        return Response(output, 200)


class StatHealthViewSetBack(BaseAPIView, ModelViewSet):
    queryset = Metrics.objects.filter().order_by("-date_created")
    serializer_class = StatsHealthSerializer
    # permission_classes = [AllowAny]

    http_method_names = ["get"]
    # lookup_field = "id"

    def list(self, request, *args, **kwargs):
        """
        List all stats health
        """
        data = []
        slugs = [
            "pageFans",
            "totalPostReactions",
            "totalLikePostReactions",
            "postCount",
            "pageFollowers",
            "postLikes",
            "pagePosts",
            "pageFollower",
            "pageTweet",
            "postReactions",
            "postCount",
            "favourites_count",
            "pagePostEngagement",
            "postEngagement",
            "pageEngagement",
        ]
        metricNames = {
            "linkedin": "Post Engagement,Followers,Posts",
            "facebook": "Page Post Engagement,Fans,Posts",
            "twitter": "Engagement,Followers,Tweets",
            "instagram": "Post Comments, Post Likes",
        }
        page_details = {}
        params = {
            "account__user_id": request.auth_user_id,
            "account__status__in": ["active", "revoked"],
        }
        for platform in Account.objects.filter(
            user_id=request.auth_user_id
        ).values_list("type", flat=True):
            data = {
                "breakdown": "page",
                "platform": platform,
                "name": metricNames[platform],
            }
            serializer = MetricPostFilterSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            data = serializer.data
            page_ids = MetricComputation.get_all_pages(
                request.auth_user_id, data["platform"]
            )
            (
                filter_slugs,
                custom_slugs,
                agg_post,
                attributes,
            ) = MetricComputation.get_slugs(data["name"], data)
            output = MetricComputation.get_metrics(
                (filter_slugs, custom_slugs, agg_post),
                data,
                request.auth_user_id,
                page_ids,
            )
        # check cache
        CACHE_KEY = f"stat_health_{request.auth_user_id}"
        output = False  # Cacher.get(CACHE_KEY)
        if not output:
            # params["account__page_id__in"] = ["100281786832302", "101493304898267"]
            # params["account__page_id__in"] = ["1073889170320351233"]
            account_metrics = AccountMetrics.objects.select_related(
                "metrics", "account"
            ).filter(**params, **{"metrics__slug__in": slugs})
            account_objects = list(
                AccountObject.objects.select_related("account")
                .filter(**params)
                .values(
                    "account__page_id",
                    "account__name",
                    "account__type",
                    "date_posted",
                    "object_id",
                    "data",
                )
            )
            account_objects = pd.DataFrame(account_objects)

            account_metrics = list(
                account_metrics.values(
                    "account__page_id",
                    "account__name",
                    "account__type",
                    "metrics__name",
                    "account__data",
                    "metrics__slug",
                    "value",
                    "date",
                )
            )
            account_metrics = pd.DataFrame(account_metrics)
            groups = account_metrics.groupby(["account__page_id", "metrics__slug"])
            for key, group in groups:
                page_id = key[0]
                slug = key[1]
                # if slug == "pageFollower" and page_id == "7582043":
                #     print("so here", key, group)
                name = group["metrics__name"].values[0]
                row = group.loc[group.date == group["date"].max()]
                value = 0
                if row.empty:
                    if slug == "totalPostReactions":
                        value = group.value.apply(
                            lambda x: sum(_to_int(ast.literal_eval(x).values()))
                        ).sum()
                        # get post likes
                        # print(group.value)
                        likes = group.value.apply(
                            lambda x: ast.literal_eval(x).get("like", 0)
                        ).sum()
                        # print("likes", likes)
                        tmp = {"page_id": page_id, "_Post Likes": likes}
                        data.append(tmp)
                    elif slug in ["pageFollower", "postLikes"]:
                        tmp = {
                            "page_id": page_id,
                            name: group["value"].apply(lambda x: int(x)).sum(),
                        }
                        data.append(tmp)
                else:
                    value = row["value"].values[0]

                profile_pic_url = ""
                pp = group["account__data"].values[0]
                if pp:
                    profile_pic_url = pp.get("profile_pic_url", "")
                tmp = {"page_id": page_id, name: int(value)}

                if page_id not in page_details:
                    page_details[page_id] = {
                        "page_id": page_id,
                        "page_name": group["account__name"].values[0],
                        "picture_url": profile_pic_url,
                        "platform": group["account__type"].values[0],
                    }

                data.append(tmp)

            df = pd.DataFrame(data)
            # print("1--",df[df["page_id"] == "1073889170320351233"])
            df = df.fillna(0)
            # print(df.to_dict())
            # print("2--", df[df["page_id"] == "1073889170320351233"])
            df = df.groupby("page_id").agg("sum")
            # print("GROUPED BY ::", df)
            # print("3--",df[df["page_id"] == "1073889170320351233"])
            df = df.reset_index()
            # print("4--",df[df["page_id"] == "1073889170320351233"])
            df["Posts"] = df.apply(
                lambda x: account_objects[
                    account_objects["account__page_id"] == x["page_id"]
                ].shape[0],
                axis=1,
            )

            df = df.drop_duplicates()
            # print("final:",df[df["page_id"] == "1073889170320351233"])
            df2 = pd.DataFrame(list(page_details.values()))
            df = pd.concat([df, df2], axis=1, join="inner")

            # postlikes
            df["Post Likes"] = df.apply(
                lambda x: get_post_likes(x, account_objects, page_details), axis=1
            )
            df["Page Fans"] = df.apply(lambda x: get_fans(x, page_details), axis=1)
            df["Post Reactions"] = df.apply(
                lambda x: get_post_reactions(x, page_details), axis=1
            )
            # print("df")
            # print(df[df["platform"] == "twitter"])

            # df = df.drop(
            #     ["Fans", "Followers", "Post Reactions: Like", "_Post Likes"], axis=1
            # )
            for col in ["Fans", "Followers", "Post Reactions: Like", "_Post Likes"]:
                if col in df.columns:
                    df = df.drop(columns=col, axis=1)

            # df_new = df.rename(columns={'A': 'a'}, index={'ONE': 'one'})
            output = df.to_dict("records")  # df.to_dict('index')
            Cacher.set(CACHE_KEY, output)

        return Response(output, 200)
