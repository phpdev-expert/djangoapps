import ast
import logging
from webapp.apps.metrics.analytics.mapping import COUNTRY_CODE, LANG_CODE
from webapp.apps.metrics.analytics import MetricComputation
from itertools import groupby

import pandas as pd

log = logging.getLogger("metric")

computations = [
    "pageFansGenderAge",
    "pageFansCountry",
    "pageFansLocale",
    "pageNegativeFeedbackByType",
    "pageReactions",
]

breakdown_comparisons = [
    "organicvspaid",
    "manualvsauto",
    "repeatvsunique"
]

def get_value(x):
    value = x
    if type(value) == dict:
        value = FacebookAnalytics.get_dict_sum(value)
    if type(value) == float:
        value = round(value, 2)
    return value


def get_post_data(x):
    data = {}
    try:
        if x["object_id__object_id"]:
            data = {
                "post_id": x["object_id__object_id"],
                "title": x["object_id__title"],
                "date": x["object_id__date_posted"],
            }
    except Exception as ex:
        print(ex)
    return data


class FacebookAnalytics:
    @staticmethod
    def get_dict_sum(raw_value):
        _sum = 0
        try:
            for k, v in raw_value.items():
                _sum += int(v)
        except Exception:
            pass
        return _sum

    @staticmethod
    def get_mapping(raw_value, MAP):
        value = {}
        try:
            for k, v in raw_value.items():
                name = MAP.get(k)
                value[name] = v
        except Exception:
            pass
        return value

    @staticmethod
    def get_sum_or_as_is(raw_value, breakdown):
        value = {}
        if breakdown == "type":
            value = raw_value
        else:
            value = FacebookAnalytics.get_dict_sum(raw_value)
        return value

    @staticmethod
    def compute_pageFansGenderAge(raw_value, rules):
        breakdown = rules["breakdown"]
        value = {}
        if breakdown == "age":
            value = {
                "13-17": 0,
                "18-24": 0,
                "25-34": 0,
                "35-44": 0,
                "45-54": 0,
                "55-64": 0,
                "65+": 0,
            }
            try:
                for k, v in raw_value.items():
                    d = k.split(".")[-1]
                    value[d] += int(v)

            except Exception as ex:
                print(ex)

        elif breakdown == "gender":
            value = {"m": 0, "f": 0, "u": 0}
            try:
                for k, v in raw_value.items():
                    d = k.split(".")[0].lower()
                    value[d] += int(v)

            except Exception as ex:
                print(ex)

        return value

    @staticmethod
    def compute_pageFansCountry(raw_value, rules):
        return FacebookAnalytics.get_mapping(raw_value, COUNTRY_CODE)

    @staticmethod
    def compute_pageFansLocale(raw_value, rules):
        return FacebookAnalytics.get_mapping(raw_value, LANG_CODE)

    @staticmethod
    def compute_pageNegativeFeedbackByType(raw_value, rules):
        value = {}
        try:
            for k, v in raw_value.items():
                k = k.replace("_", " ").title()
                value[k] = v
        except Exception:
            pass
        return value

    @staticmethod
    def compute_pageReactions(raw_value, rules):
        breakdown = rules["breakdown"]
        value = FacebookAnalytics.get_sum_or_as_is(raw_value, breakdown)
        return value

    @staticmethod
    def compute(group, rules, agg_post):
        slug = group.head(1)["metrics__slug"].values[0]
        try:
            group["value"] = group["value"].apply(lambda x: ast.literal_eval(x))
            group["data"] = group["value"].apply(lambda x: {})
            if slug in computations:
                group["value"] = group["value"].apply(
                    lambda x: getattr(FacebookAnalytics, f"compute_{slug}")(x, rules)
                )
            else:
                if rules["breakdown"] == "post":
                    group["value"] = group["value"].apply(lambda x: get_value(x))

                if "sum" in rules["agg"]:
                    group["value"] = group["value"].apply(
                        lambda x: FacebookAnalytics.get_dict_sum(x)
                    )

        except Exception as ex:
            print(ex)
        return group


def filter_post_data(data, acc, obj_id):
    json_data = {"media": [], "permalink": None}
    if "media" in data.keys():
        json_data["media"] = data["media"]
    if acc["type"] == "twitter":
        json_data[
            "permalink"
        ] = f"https://twitter.com/{acc['name']}/status/{obj_id}"
    elif acc["type"] == "facebook":
        json_data["permalink"] = "https://facebook.com/{}".format(
            obj_id
        )
    elif acc["type"] == "linkedin":
        json_data["permalink"] = "https://linkedin.com/feed/update/{}".format(
            obj_id
        )

    return json_data


class FacebookMetricComputation:
    def get_metrics_mapping(
            self, account_metrics, rules={"breakdown": None, "agg": "As is"}, agg_post=False
    ):
        account_metrics_mapping = {}
        if not account_metrics:
            return account_metrics_mapping
        account_metrics = list(
            account_metrics.values(
                "account__page_id",
                "account__type",
                "account__name",
                "value",
                "value_type",
                "date",
                "metrics__slug",
                "metrics__name",
                "metrics__platform",
                "object_id__object_id",
                "object_id__title",
                "object_id__date_posted",
                "object_id__data"
            )
        )

        account_metrics = pd.DataFrame(account_metrics)
        all_groups = account_metrics.groupby(
            ["account__page_id", "metrics__slug"]
        ).apply(lambda group: FacebookAnalytics.compute(group, rules, agg_post))

        # all_groups = all_groups.drop(['object_id__object_id',
        # 'object_id__title', 'object_id__date_posted'], axis = 1)
        for i in all_groups["account__page_id"].unique():
            account_metrics_mapping[i] = [
                {
                    "slug": all_groups["metrics__slug"][j],
                    "name": all_groups["metrics__name"][j],
                    "date": all_groups["date"][j],
                    "value": all_groups["value"][j],
                    "data": {
                        "post_id": all_groups["object_id__object_id"][j],
                        "title": all_groups["object_id__title"][j],
                        "date": all_groups["object_id__date_posted"][j],
                        "data": filter_post_data(all_groups["object_id__data"][j],
                                                 {"name": all_groups["account__name"][j],
                                                  "page_id": all_groups["account__page_id"][j],
                                                  "type": all_groups["account__type"][j]},
                                                 all_groups["object_id__object_id"][j]),
                    }
                    if agg_post and rules["agg"] not in ["post"]
                    else all_groups["data"][j],
                }
                for j in all_groups[all_groups["account__page_id"] == i].index
            ]

        if rules["breakdown"] not in ["page", "post"]:
            account_metrics_mapping = MetricComputation.get_sum_across_page(
                account_metrics_mapping
            )
            if rules["breakdown"] in breakdown_comparisons:
                account_metrics_mapping.sort(key=lambda content: (content['date'], content['name']))
                group_output = []
                for groupset, group in groupby(account_metrics_mapping, lambda content: (content['date'],content['name'])):
                    row = {}
                    row["date"] = groupset[0]
                    row["name"] = groupset[1]
                    row["value"] = {}
                    for item in group:
                        if item["slug"] in row["value"]:
                            row["value"][item["slug"]] += item["value"]
                        else:
                            row["value"].update({item["slug"]:item["value"]})
                    group_output.append(row)
                account_metrics_mapping = group_output


            return account_metrics_mapping

        if agg_post and rules["agg"] == "post":
            am = {}
            for page_id, rows in account_metrics_mapping.items():

                if page_id not in am:
                    am[page_id] = [rows[0]]
                    am[page_id][0]["value"] = 0

                for row in rows:
                    value = row["value"]
                    if type(value) == dict:
                        value = FacebookAnalytics.get_dict_sum(value)
                    # elif type(value) == float:
                    #     value = round(value, 2)
                    else:
                        try:
                            value = int(value)
                        except Exception:
                            value = 0

                    am[page_id][0]["value"] += value
            account_metrics_mapping = am
        return account_metrics_mapping
