from webapp.apps.metrics.models import AccountMetrics, AccountObject, Metrics, PostComments, CommentReplies

import logging
from datetime import datetime, timedelta
from webapp.apps.metrics.analytics import MetricComputation

log = logging.getLogger("metric")


computations = [
    "pageInboundMessages",
    "pagePostComments",
    "postLikes",
    "pagePosts",
    "postTable",
]


class InstagramAnalytics:
    @staticmethod
    def get_date_params(input_params, date_field):
        params = {}
        if "since" in input_params:
            params[f"{date_field}__gte"] = input_params["since"]
        if "until" in input_params:
            params[f"{date_field}__lte"] = (datetime.strptime(
                input_params["until"], "%Y-%m-%d"
            ) + timedelta(days=1)).strftime("%Y-%m-%d")

        return params

    @staticmethod
    def compute_pageInboundMessages(posts, rules, m=None):
        metrics = {}

        for p in posts:
            value = []
            comments = PostComments.objects.filter(
                object=p
            )
            value += comments.values("author", "message", "date")
            value += list(
                CommentReplies.objects.filter(
                    comment__in=comments
                ).values("author", "message", "date")
            )
            #comments = p.data.get("comments", [])
            # value = []
            # for c in comments:
            #     value.append({
            #         "author":c.get("username", ""),
            #         "date":c.get("timestamp", ""),
            #         "message":c.get("text", "")
            #     })
            tmp = {
                "value": value,
                "date": p.date_posted,
                "slug": m.slug,
                "name": m.name,
            }
            metrics.setdefault(p.account.page_id, []).append(tmp)

        return metrics

    @staticmethod
    def compute_pagePostComments(posts, rules, m=None):
        breakdown = rules["breakdown"]
        metrics = {}

        if breakdown == "type":
            # group comment based on media type
            comments_count = {}
            for p in posts:
                page_id = p.account.page_id
                comments_count.setdefault(page_id, {})
                #comments = p.data.get("comments", [])
                media_type = p.data.get("media_type", None)
                if media_type:
                    count = p.data.get("comments_count", 0) #len(comments)
                    if media_type not in comments_count[page_id]:
                        comments_count[page_id][media_type] = count
                    else:
                        comments_count[page_id][media_type] += count
            for k, v in comments_count.items():
                tmp = {"value": v, "slug": m.slug, "name": m.name, "date": ""}
                metrics.setdefault(k, []).append(tmp)


        else:
            comments_count = 0
            for p in posts:
                #comments = p.data.get("comments", [])
                comments_count = p.data.get("comments_count", 0) #len(comments)
                data = {"post_id": p.object_id, "title": p.title}
                tmp = {
                    "value": comments_count,
                    "slug": m.slug,
                    "name": m.name,
                    "date": p.date_posted,
                    "data": data,
                }
                metrics.setdefault(p.account.page_id, []).append(tmp)
        return metrics

    @staticmethod
    def compute_postLikes(posts, rules, m=None):
        breakdown = rules["breakdown"]
        metrics = {}

        if breakdown == "type":
            # group like based on media type
            likes_count = {}
            for p in posts:
                page_id = p.account.page_id
                likes_count.setdefault(page_id, {})

                _likes_count = p.data.get("like_count", 0)
                media_type = p.data.get("media_type", None)
                if media_type:

                    if media_type not in likes_count[page_id]:
                        likes_count[page_id][media_type] = _likes_count
                    else:
                        likes_count[page_id][media_type] += _likes_count

            for k, v in likes_count.items():
                tmp = {"value": v, "slug": m.slug, "name": m.name, "date": ""}
                metrics.setdefault(k, []).append(tmp)

        else:
            for p in posts:
                v = p.data.get("like_count", 0)
                data = {"post_id": p.object_id, "title": p.title}
                tmp = {
                    "value": v,
                    "slug": m.slug,
                    "name": m.name,
                    "date": p.date_posted,
                    "data": data,
                }
                metrics.setdefault(p.account.page_id, []).append(tmp)
        return metrics

    @staticmethod
    def compute_pagePosts(posts, rules, m=None):
        breakdown = rules["breakdown"]
        metrics = {}

        if breakdown == "type":

            post_count = {}
            for p in posts:
                page_id = p.account.page_id
                post_count.setdefault(page_id, {})
                media_type = p.data.get("media_type", None)
                if media_type:

                    if media_type not in post_count[page_id]:
                        post_count[page_id][media_type] = 1
                    else:
                        post_count[page_id][media_type] += 1

            for k, v in post_count.items():
                tmp = {"value": v, "slug": m.slug, "name": m.name, "date": ""}
                metrics.setdefault(k, []).append(tmp)

        else:
            account_posts = {}
            for p in posts:
                page_id = p.account.page_id
                if page_id not in account_posts:
                    account_posts[page_id] = 1
                else:
                    account_posts[page_id] += 1

            for k, v in account_posts.items():
                tmp = {"value": v, "slug": m.slug, "name": m.name, "date": ""}
                metrics.setdefault(k, []).append(tmp)

        return metrics

    @staticmethod
    def compute_postTable(posts, rules, m=None):
        metrics = {}
        for p in posts:
            page_id = p.account.page_id
            tmp = {
                "value": {
                    "id": p.object_id,
                    "page_id": page_id,
                    "date_posted": p.date_posted,
                    "title":p.title,
                    "description": p.description,
                    "data": {
                        "media_url": p.data.get("media_url", ""),
                        "media_type": p.data.get("media_type", ""),
                        "message": p.description,
                        "like_count": p.data.get("like_count", 0),
                        "comment_count": p.data.get("comments_count", 0),
                    },
                },
                "slug": m.slug,
                "name": m.name,
                "date": "",
            }
            metrics.setdefault(page_id, []).append(tmp)
        return metrics

    @staticmethod
    def compute(slugs, accounts, data):
        rules = {"breakdown": data["breakdown"], "agg": data["aggregration"]}
        metrics = {}
        account_object_slugs = []
        _mm = Metrics.objects.filter(platform="instagram", slug__in=slugs)
        for m in _mm:
            slug = m.slug
            if slug in computations:
                date_params = InstagramAnalytics.get_date_params(data, "date_posted")
                posts = AccountObject.objects.select_related("account").filter(
                    account__in=accounts, object_type="post", **date_params
                )
                _metrics = getattr(InstagramAnalytics, f"compute_{slug}")(
                    posts, rules, m
                )
                for k, v in _metrics.items():
                    if k not in metrics.keys():
                        metrics[k] = []
                    metrics[k] += v
            else:
                account_object_slugs.append(slug)

        if account_object_slugs:

            params = {
                "account__in": accounts,
                "metrics__slug__in": account_object_slugs,
                "metrics__platform": "instagram",
            }
            date_params = InstagramAnalytics.get_date_params(data, "date")
            log.info("metric params : {}".format(params))
            account_metrics = AccountMetrics.objects.select_related(
                "metrics", "account"
            ).filter(**params, **date_params)
            log.info("metric queryset : {}".format(account_metrics.count()))

            for am in account_metrics:
                m = am.metrics
                tmp = {
                    "value": am.value,
                    "slug": m.slug,
                    "date": am.date,
                    "name": m.name,
                }
                metrics.setdefault(am.account.page_id, []).append(tmp)

        return metrics


class InstagramMetricComputation:
    def get_metrics_mapping(self, slugs, data, accounts):
        #print("s", slugs)
        slugs = [*{*slugs}]
        account_metrics_mapping = {}
        for a in accounts:
            account_metrics_mapping[a.page_id] = []

        metrics = InstagramAnalytics.compute(slugs, accounts, data)
        for page_id, ms in metrics.items():
            for m in ms:
                account_metrics_mapping[page_id].append(m)

        if data["breakdown"] not in ["page", "post"]:
            account_metrics_mapping = MetricComputation.get_sum_across_page(
                account_metrics_mapping
            )
            return account_metrics_mapping
        return account_metrics_mapping
