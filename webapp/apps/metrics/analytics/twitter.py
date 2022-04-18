from webapp.apps.api.serializers.accounts import InboundTableSerialzer

import logging
from datetime import datetime, timedelta

log = logging.getLogger("metric")


computations = [
    "receivedDm",
    "inboundMessageTable",
    "inboundMessage",
    "postLikes",
    "postRetweet",
    "postReply",
    "tweetTable",
    "pageTweet",
    "pageMention",
    "pageEngagement",
]


class TwitterAnalytics:
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
    def compute_pageMention(mentions, rules, m=None, account_metrics_mapping={}):

        mention = {item["account__page_id"]: item["count"] for item in mentions}
        for page_id, count in mention.items():
            metric = {"value": count, "date": "", "slug": m, "name": m}
            account_metrics_mapping.setdefault(str(page_id), []).append(metric)

        return account_metrics_mapping

    @staticmethod
    def compute_pageEngagement(
        metrics, reply, rules, m=None, account_metrics_mapping={}
    ):
        data_dict = {}
        if rules.get("breakdown") == 'type':
            for metric in metrics:
                data_dict[metric.account.page_id] = data_dict.setdefault(metric.account.page_id, {})
                if metric.metrics.name in data_dict[metric.account.page_id]:
                    data_dict[metric.account.page_id][metric.metrics.name] += int(metric.value)
                else:
                    data_dict[metric.account.page_id].update({metric.metrics.name: int(metric.value) })
            for r in reply:
                data_dict[r["account__page_id"]] = data_dict.setdefault(r["account__page_id"], {})
                if "reply" in data_dict[r["account__page_id"]]:
                    data_dict[r["account__page_id"]]["reply"] += int(r["reply"])
                else:
                    data_dict[r["account__page_id"]].update({"reply": int(r["reply"]) })
        else:
            for metric in metrics:
                count = data_dict.setdefault(metric.account.page_id, 0)
                data_dict[metric.account.page_id] = count + int(metric.value)
            for r in reply:
                count = data_dict.setdefault(r["account__page_id"], 0)
                data_dict[r["account__page_id"]] = count + r["reply"]
        for page_id, value in data_dict.items():
            metric = {"value": value, "date": "", "slug": m, "name": m}
            account_metrics_mapping.setdefault(str(page_id), []).append(metric)
        return account_metrics_mapping

    @staticmethod
    def compute_postLikes_postRetweet(
        metrics, rules, m=None, agg_post=False, account_metrics_mapping={}
    ):

        if agg_post and rules["agg"] != "post":
            for metric in metrics:
                page_id = metric.account.page_id
                data = {
                    "value": metric.value,
                    "slug": m,
                    "name": m,
                    "date": metric.date,
                }

                if metric.object_id:
                    obj = metric.object_id

                    data["data"] = {
                        "post_id": obj.object_id,
                        "title": obj.title,
                        "date": obj.date_posted,
                    }
                if page_id not in account_metrics_mapping:
                    account_metrics_mapping[page_id] = []

                account_metrics_mapping[page_id].append(data)
        else:
            data_dict = {}
            for metric in metrics:
                count = data_dict.setdefault(metric.account.page_id, 0)
                data_dict[metric.account.page_id] = count + int(metric.value)
            for page_id, value in data_dict.items():
                data = {"value": value, "date": "", "slug": m, "name": m}
                account_metrics_mapping.setdefault(str(page_id), []).append(data)
        return account_metrics_mapping

    @staticmethod
    def compute_postReply(
        posts, rules, m=None, agg_post=False, account_metrics_mapping={}
    ):

        if agg_post and rules["agg"] != "post":

            for post in posts:
                page_id = post["account__page_id"]
                metric = {
                    "value": post["reply"],
                    "slug": m,
                    "name": m,
                    "date": post["date_posted"],
                }
                metric["data"] = {
                    "post_id": post["object_id"],
                    "title": post["title"],
                    "date": post["date_posted"],
                }
                if page_id not in account_metrics_mapping:
                    account_metrics_mapping[page_id] = []

                account_metrics_mapping[page_id].append(metric)
        else:
            post_dict = {}
            for post in posts:
                count = post_dict.setdefault(post["account__page_id"], 0)
                post_dict[post["account__page_id"]] = count + post["reply"]
            for page_id, value in post_dict.items():
                metric = {"value": value, "date": "", "slug": m, "name": m}
                account_metrics_mapping.setdefault(str(page_id), []).append(metric)
        return account_metrics_mapping

    @staticmethod
    def compute_inboundMessage(
        inbound_table, account_metrics_mapping, rules, m=None, agg_post=False
    ):

        for inbound in inbound_table:
            metric = {
                "value": inbound["inbox"] + inbound["mention"],
                "date": "",
                "slug": m,
                "name": m,
            }
            account_metrics_mapping.setdefault(inbound["page_id"], []).append(metric)
        return account_metrics_mapping

    # def compute_inboundMessageTable(
    #     inbound_table, rules, m=None, agg_post=False, account_metrics_mapping={}
    # ): commented by shyam - default argument for account_metrics_mapping on static method retains the value
    @staticmethod
    def compute_inboundMessageTable(
                inbound_table, account_metrics_mapping, rules, m=None, agg_post=False
        ):
        data = InboundTableSerialzer(inbound_table, many=True).data
        message_dict = {}

        for message in data:
            page_id = message.pop("page_id")
            message_dict.setdefault(page_id, []).append(message)
        for page_id, message in message_dict.items():
            metric = {"value": message, "date": "", "slug": m, "name": m}
            account_metrics_mapping.setdefault(page_id, []).append(metric)

        return account_metrics_mapping
