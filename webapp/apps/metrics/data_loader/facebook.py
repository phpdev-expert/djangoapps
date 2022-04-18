import json
from datetime import datetime, timedelta
from django.conf import settings
from django.db.models import Q
from facebook import GraphAPIError
from webapp.base.exceptions import EmptyData, MetricsNotSpecified
from webapp.apps.metrics.models import (
    Account,
    AccountMetrics,
    Metrics,
    AccountObject,
    AccountInbox,
    PostComments,
    CommentReplies,
)
from webapp.apps.metrics.data_loader import InputDataLoader
import logging
import math
import sys
from urllib.parse import urlparse, urlencode, parse_qs, urlunparse

log = logging.getLogger("facebook")


class FacebookDataLoader(InputDataLoader):
    def __init__(self, user_id, page_id):
        self.user_id = user_id
        self.page_id = page_id

    def perform_batch_request(self, batch, output=[]):
        sub_batch = []
        count = 1
        if len(batch) > 50:
            count = math.ceil(len(batch) / 50)
        for sub_batch_count in range(count):
            sub_batch.append(batch[sub_batch_count::count])

        paginations = []
        for item in sub_batch:
            #output += self.fetch_bulk_data(self.user_id, self.page_id, json.dumps(item))
            batch_response = self.get_graph_api(
                user_id=self.user_id, page_id=self.page_id
            ).request("", post_args = {"batch":json.dumps(item)}) #put_object(parent_object="/", connection_name="", batch=json.dumps(item))
            for response in batch_response:
                body = json.loads(response["body"])
                if "error" in body:
                    print(item)
                    print(body)
                    return
                output += body["data"]
                if "paging" in body:
                    _next = body["paging"].get("next", False)
                    if _next:
                        relative_url = _next.replace('https://graph.facebook.com/v3.2/','')
                        uu = list(urlparse(relative_url))
                        qs = parse_qs(uu[4], keep_blank_values=True)
                        del (qs['access_token'])
                        uu[4] = urlencode(qs, doseq=True)
                        relative_url = urlunparse(uu)
                        paginations.append(
                            {
                                "method": "GET",
                                "relative_url": relative_url,
                            }
                        )
        if paginations:
            self.perform_batch_request(paginations, output)

        # out_file = open("myfile.json", "w")
        # json.dump(output, out_file, indent=6)
        # out_file.close()

        return output

    def fetch_initial_syc(self, url):
        since = settings.SYNC_SINCE
        until = (datetime.strptime(since, "%Y-%m-%d") + timedelta(days=30)).strftime(
            "%Y-%m-%d"
        )
        repeat_to_fetch = True
        batch = []
        while repeat_to_fetch:
            if datetime.strptime(since, "%Y-%m-%d") >= datetime.today():
                break
            if datetime.strptime(until, "%Y-%m-%d") > datetime.today():
                until = datetime.today().strftime("%Y-%m-%d")
                repeat_to_fetch = False
            date_formatted_url = url + "&since={}&until={}".format(since, until)
            batch.append(
                {
                    "method": "GET",
                    "relative_url": date_formatted_url
                }
            )
            #print(date_formatted_url)
            # data += self.fetch_graph_data(
            #     self.user_id, self.page_id, date_formatted_url
            # )
            since = (datetime.strptime(until, "%Y-%m-%d") + timedelta(days=1)).strftime(
                "%Y-%m-%d"
            )
            until = (
                datetime.strptime(since, "%Y-%m-%d") + timedelta(days=30)
            ).strftime("%Y-%m-%d")

        return batch

    def save_page(self, data):
        page, c = Account.objects.get_or_create(
            type="facebook", page_id=self.page_id, user_id=self.user_id
        )
        data_dict = {}
        if data.get("name"):
            page.name = data.get("name")
        page.status = data.get("status")
        if data.get("access_token"):
            page.token = data.get("access_token")
        if data.get("picture_url"):
            data_dict.update({"profile_pic_url": data.get("picture_url")})
            page.data = data_dict
        page.save()
        return c

    def prepare_metrics(self, data, extracted_metrics):
        # body = json.loads(response["body"])
        # if "error" in body:
        #     return extracted_metrics
        #     # raise GraphAPIError(body)
        # data = body["data"]
        if not data:
            return extracted_metrics
            # raise EmptyData
        for datum in data:
            name = datum["name"]
            period = datum["period"]
            if period not in ["day", "lifetime"]:
                continue
            if name not in extracted_metrics:
                extracted_metrics[name] = {}
            extracted_metrics[name][period] = datum["values"]
            if "id" in datum:
                extracted_metrics[name]["id"] = datum["id"]
        return extracted_metrics

    def fetch_page_insights(self, graph_id, metrics, params={"initial_sync": False}):
        if not metrics:
            raise MetricsNotSpecified("Specify metrics you want to fetch.")

        metric_joined = ""
        for metric in metrics:
            metric_joined += "'{}',".format(metric)
        relative_url = "{}/insights/?metric=[{}]".format(graph_id, metric_joined)
        if params["initial_sync"]:
            batch = self.fetch_initial_syc(relative_url)
            data = self.fetch_bulk_data(self.user_id, self.page_id, batch)
            # relative_url = relative_url + "&since="+settings.SYNC_SINCE
        else:

            if "since" in params:
                relative_url = relative_url + "&since=" + params["since"]
            if "until" in params:
                diff = datetime.strptime(
                    params["until"], "%Y-%m-%d"
                ) - datetime.strptime(params["since"], "%Y-%m-%d")
                if diff.days < 90:
                    relative_url = relative_url + "&until=" + params["until"]
            print(relative_url)
            data = self.fetch_graph_data(self.user_id, self.page_id, relative_url)
        # request_data = {"method": "GET", "relative_url": relative_url}
        # batch = [request_data]
        #
        # batch_response = self.get_graph_api(self.user_id, graph_id).put_object(
        #     parent_object="/", connection_name="", batch=json.dumps(batch)
        # )
        extracted_metrics = {}
        # response = batch_response[0]
        # body = json.loads(response["body"])
        # if "error" in body:
        #     raise GraphAPIError(body)
        # data = body["data"]
        if not data:
            raise EmptyData
        for datum in data:
            name = datum["name"]
            period = datum["period"]
            if period not in ["day", "lifetime"]:
                continue
            if name not in extracted_metrics:
                extracted_metrics[name] = {}
            if period in extracted_metrics[name]:
                extracted_metrics[name][period] += datum["values"]
            else:
                extracted_metrics[name][period] = datum["values"]
        return extracted_metrics

    def fetch_fb_posts(self, params={"initial_sync": False}):
        # url = "{}/posts".format(self.page_id)
        # permalink_url = to get post url
        url = "me/published_posts?fields=message,attachments{url,media,media_type},comments{comment_count},likes.summary(true),shares,created_time,id&summary=total_count&period=day"  # noqa E501
        if params["initial_sync"]:
            url = url + "&since=" + settings.SYNC_SINCE
        else:
            if "since" in params:
                url = url + "&since=" + params["since"]
            if "until" in params:
                diff = datetime.strptime(
                    params["until"], "%Y-%m-%d"
                ) - datetime.strptime(params["since"], "%Y-%m-%d")
                if diff.days < 90:
                    url = url + "&until=" + params["until"]
        print(url)
        output = self.fetch_graph_data(self.user_id, self.page_id, url)
        return output
        # batch = [{"method": "GET", "relative_url": url}]
        # batch_response = self.get_graph_api(
        #     user_id=self.user_id, page_id=self.page_id
        # ).put_object(parent_object="/", connection_name="", batch=json.dumps(batch))
        # #print(batch_response)
        # response = batch_response[0]
        # body = json.loads(response["body"])
        # if "error" in body:
        #     raise GraphAPIError(body)
        # data = body["data"]
        # if not data:
        #     raise EmptyData
        # return body["data"]

    def fetch_facebook_videos(self, params={"initial_sync": False}):
        url = f"{self.page_id}/videos"
        if params["initial_sync"]:
            url = url + "&since=" + settings.SYNC_SINCE
        else:
            if "since" in params:
                url = url + "&since=" + params["since"]
            if "until" in params:
                url = url + "&until=" + params["until"]

        output = self.fetch_graph_data(self.user_id, self.page_id, url)
        return output

        # batch = [{"method": "GET", "relative_url": url}]
        #
        # response = self.get_graph_api(self.user_id, self.page_id).put_object(
        #     parent_object="/", connection_name="", batch=json.dumps(batch)
        # )
        #
        # return json.loads(response[0].get("body")).get("data")

    def fetch_insights(self, params={"initial_sync": False}):
        account = Account.objects.get(page_id=self.page_id, user_id=self.user_id)

        # first fetch page level metrics with /me/insights
        metrics = (
            Metrics.objects.filter(
                Q(platform="facebook")
                & Q(fields__level="page")
                & Q(fields__endpoint="me/insights")
            )
            .exclude(metric__exact="")
            .exclude(metric__exact="null")
        )

        all_metrics = list(metrics.values_list("metric", flat=True))
        metric_ids = {}
        for m in metrics:
            metric_ids[m.metric] = m.id

        try:
            # print(all_metrics)
            metrics = self.fetch_page_insights(self.page_id, all_metrics, params)
        except Exception as ex:
            update = ["sync_status", "error"]
            if isinstance(ex, GraphAPIError):
                account.status = "revoked"
                update.append("status")
            self.flag = False
            account.sync_status = "failed"
            account.error = str(ex)
            account.save(update_fields=update)
            log.info(ex)
        else:
            create_objects = []
            update_objects = []
            for metric, records in metrics.items():
                for period, values in records.items():
                    for row in values:
                        # log.info(row)
                        if "end_time" in row:
                            try:
                                o = AccountMetrics.objects.get(
                                    account=account,
                                    metrics_id=metric_ids[metric],
                                    date=row["end_time"],
                                )
                                o.value = row["value"]
                                update_objects.append(o)
                            except Exception as err:  # noqa E722
                                create_objects.append(
                                    AccountMetrics(
                                        account=account,
                                        metrics_id=metric_ids[metric],
                                        date=row["end_time"],
                                        value_type=type(row["value"]).__name__,
                                        value=row["value"],
                                    )
                                )
                        else:
                            log.info(f"end_time not present -{metric}-{period}-{row}")

            AccountMetrics.objects.bulk_create(create_objects)
            AccountMetrics.objects.bulk_update(update_objects, ["value"])
        # if self.flag:
        #     #account.sync_status = "ok"
        #     account.error = ""
        #     account.save()

    def get_day_metrics(self, post_id, metric_objects, params={"initial_sync": False}):
        daily_metrics = ""
        batch = []
        for m in metric_objects:
            if m.fields["period"] == "day":
                daily_metrics += '"{}",'.format(m.metric)
        if params["initial_sync"]:
            return self.fetch_initial_syc("{}/insights?period=day&metric=[{}]".format(
                    post_id, daily_metrics
                ))
        batch.append(
            {
                "method": "GET",
                "relative_url": "{}/insights?period=day&metric=[{}]".format(
                    post_id, daily_metrics
                ),
            }
        )
        return batch

    def get_lifetime_metrics(self, post_id, metric_objects, params={"initial_sync": False}):
        lifetime_metrics = ""
        batch = []
        for m in metric_objects:
            if m.fields["period"] != "day":
                lifetime_metrics += '"{}",'.format(m.metric)

        batch.append(
            {
                "method": "GET",
                "relative_url": "{}/insights?period=lifetime&metric=[{}]".format(
                    post_id, lifetime_metrics
                ),
            }
        )
        return batch

    def get_post_table(self, post_id, metric_objects, params={"initial_sync": False}):
        daily_metrics = ""
        lifetime_metrics = ""
        extracted_metrics = {}
        batch = []
        for m in metric_objects:
            if m.fields["period"] == "day":
                daily_metrics += '"{}",'.format(m.metric)
            else:
                lifetime_metrics += '"{}",'.format(m.metric)

        # print("day", '{}/insights?period=day&metric=[{}]'.format(post_id, daily_metrics))
        batch.append(
            {
                "method": "GET",
                "relative_url": "{}/insights?period=lifetime&metric=[{}]".format(
                    post_id, lifetime_metrics
                ),
            }
        )
        if params["initial_sync"]:
            batch += self.fetch_initial_syc("{}/insights?period=day&metric=[{}]".format(
                    post_id, daily_metrics
                ))
        else:
            batch.append(
                {
                    "method": "GET",
                    "relative_url": "{}/insights?period=day&metric=[{}]".format(
                        post_id, daily_metrics
                    ),
                }
            )
        #return batch
        # batch = [
        #     {
        #         "method": "GET",
        #         "relative_url": "{}/insights?period=lifetime&metric=[{}]".format(
        #             post_id, lifetime_metrics
        #         ),
        #     },
        #     {
        #         "method": "GET",
        #         "relative_url": "{}/insights?period=day&metric=[{}]".format(
        #             post_id, daily_metrics
        #         ),
        #     },
        # ]
        try:
            batch_response = self.fetch_bulk_data(self.user_id, self.page_id, batch)
            # batch_response = self.get_graph_api(
            #     user_id=self.user_id, page_id=self.page_id

            # ).put_object(parent_object="/", connection_name="", batch=json.dumps(batch))
            # url = "{}/insights?period=lifetime&metric=[{}]".format(
            #     post_id, lifetime_metrics
            # )
            # print(url)
            #output = self.fetch_graph_data(self.user_id, self.page_id, url, 125)
            # print(output)
            #metrics = self.prepare_metrics(output, extracted_metrics)
            extracted_metrics = self.prepare_metrics(batch_response, extracted_metrics)
            #extracted_metrics.update(metrics)

            # url = "{}/insights?period=day&metric=[{}]".format(post_id, daily_metrics)
            # print(url)
            # output = self.fetch_graph_data(self.user_id, self.page_id, url, 125)
            # print(output)
            # print(extracted_metrics)
            # metrics = self.prepare_metrics(output, extracted_metrics)
            # metrics = self.prepare_metrics(batch_response[1], extracted_metrics)
            # extracted_metrics.update(metrics)
            # print("ex", extracted_metrics)
            # comments = batch_response[1]
            # comments = json.loads(comments["body"])["data"]

            # shares = batch_response[2]
            # shares = json.loads(shares["body"])["data"]

            # extracted_metrics["PostCommentCount"] = {"lifetime": [{"value": len(comments)}]}
            # extracted_metrics["PostShareCount"] = {"lifetime": [{"value": len(shares)}]}
        except Exception as e:
            print(e)
            pass
        return extracted_metrics

    def get_post_share_comment(self, post):
        sc = {"comment_count": 0, "share_count": 0, "likes_count": 0}
        comments = post.get("comments", {})
        comments = comments.get("data", [])
        for c in comments:
            sc["comment_count"] += int(c["comment_count"])

        shares = post.get("shares", {})
        sc["share_count"] += shares.get("count", 0)
        if "likes" in post:
            if "summary" in post["likes"]:
                sc["likes_count"] = post["likes"]["summary"].get("total_count", 0)
        return sc

    def sync_post_and_video(self, object_type, params):
        print("sync post")
        page = Account.objects.get(page_id=self.page_id, user_id=self.user_id)
        metric_objects = (
            Metrics.objects.filter(Q(platform="facebook") & Q(fields__level="post"))
            .exclude(metric__exact="")
            .exclude(metric__exact="null")
        )
        # all_metrics = list(metrics.values_list("metric", flat=True))
        metric_ids = {}
        for m in metric_objects:
            metric_ids[m.metric] = m.id
        posts = []
        if object_type == "post":
            posts = self.fetch_fb_posts(params)
        elif object_type == "video":
            posts = []  # self.fetch_facebook_videos()
        batchreq = []
        for p in posts:
            json_data = {}
            post_id = p.get("id")
            if object_type == "post":
                message = ""
                if "message" in p:
                    message = p.get("message")
                elif "story" in p:
                    message = p.get("story")

                post_insight = self.get_post_share_comment(p)
                json_data["comment_count"] = post_insight["comment_count"]
                json_data["share_count"] = post_insight["share_count"]
                json_data["likes_count"] = post_insight["likes_count"]
                ##check for image or video url
                if "attachments" in p:
                    if "data" in p["attachments"]:
                        media_info = p["attachments"]["data"][0]
                        if "media" in media_info:
                            json_data["media_type"] = media_info["media_type"].lower()
                            if media_info["media_type"].lower() == "video":
                                # for video get the url from source field
                                json_data["media_url"] = media_info["media"].get(
                                    "source", ""
                                )
                            elif "image" in media_info["media"]:
                                json_data["media_url"] = media_info["media"][
                                    "image"
                                ].get("src", "")

                # json_data["permalink"] = post_insight.get("permalink","")
                # try:
                #     json_data["permalink"] = json_data["permalink"].split("facebook.com/")[1]
                # except:
                #     pass

            elif object_type == "video":
                message = p.get("description")

            try:
                _post, c = AccountObject.objects.update_or_create(
                    account=page,
                    object_id=post_id,
                    object_type=object_type,
                    defaults={
                        "title": message,
                        "date_posted": p.get("created_time"),
                        "data": json_data,
                    },
                )
                metrics = {}

                if object_type == "post":
                    metrics = self.get_post_table(p["id"], metric_objects, params)
                    # metrics = self.get_day_metrics(p["id"], metric_objects, params)
                    # batchreq += metrics
                    #metrics = self.get_lifetime_metrics(p["id"], metric_objects)
                    #batchreq += metrics
                    #continue
                elif object_type == "video":
                    metrics = {}
                    # metrics = self.get_post_table(p["id"])

                for k, v in metrics.items():
                    print(v["id"].split("/")[0])
                    _post = AccountObject.objects.get(
                        object_id=v["id"].split("/")[0],
                        account=page,
                        object_type=object_type,
                    )
                    if "day" in v:
                        value = v["day"][0]["value"]
                        v["day"][0]["end_time"]

                        for row in v["day"]:
                            value = row["value"]
                            date = row["end_time"]
                            AccountMetrics.objects.update_or_create(
                                account=_post.account,
                                object_id_id=_post.id,
                                metrics_id=metric_ids[k],
                                date=date,
                                defaults={
                                    "value": value,
                                    "value_type": type(value).__name__,
                                },
                            )
                    else:
                        value = v["lifetime"][0]["value"]
                        AccountMetrics.objects.update_or_create(
                            account=_post.account,
                            object_id_id=_post.id,
                            metrics_id=metric_ids[k],
                            defaults={"value": value, "value_type": type(value).__name__, },
                            date=None,
                        )
            except Exception as ex:
                log.info(ex)
                self.flag = False
        if batchreq:
            extracted_metrics = {}
            bulkoutput = self.fetch_bulk_data(self.user_id, self.page_id, batchreq)
            extracted_metrics = self.prepare_metrics(
                bulkoutput, extracted_metrics
            )
            for k, v in extracted_metrics.items():
                print(v["id"].split("/")[0])
                _post = AccountObject.objects.get(
                    object_id=v["id"].split("/")[0],
                    account=page,
                    object_type=object_type,
                )
                if "day" in v:
                    value = v["day"][0]["value"]
                    v["day"][0]["end_time"]

                    for row in v["day"]:
                        value = row["value"]
                        date = row["end_time"]
                        AccountMetrics.objects.update_or_create(
                            account=_post.account,
                            object_id_id=_post.id,
                            metrics_id=metric_ids[k],
                            date=date,
                            defaults={
                                "value": value,
                                "value_type": type(value).__name__,
                            },
                        )
                else:
                    value = v["lifetime"][0]["value"]
                    AccountMetrics.objects.update_or_create(
                        account=_post.account,
                        object_id_id=_post.id,
                        metrics_id=metric_ids[k],
                        defaults={"value": value, "value_type": type(value).__name__,},
                        date=None,
                    )
        # # if self.flag:
        #     #page.sync_status = "ok"
        #     page.error = ""
        #     page.save()

    def save_replies(self, comment):
        url = (
            f"{comment.comment_id}/comments?fields=like_count,message,from,created_time"
        )
        # print("reply url", url)
        replies = self.fetch_graph_data(self.user_id, self.page_id, url)
        for reply in replies:
            from_info = reply.get("from", {})
            CommentReplies.objects.update_or_create(
                comment_id=comment.id,
                reply_id=reply["id"],
                defaults={
                    "date": reply["created_time"],
                    "author": from_info.get("name", ""),
                    "fields": {
                        "from": from_info,
                        "like_count": reply.get("like_count", 0),
                    },
                    "message": reply.get("message", ""),
                },
            )

    def bulk_save_replies(self, bulk_req):
        print("sync replies")
        replies = self.fetch_bulk_data(self.user_id, self.page_id, bulk_req)
        for reply in replies:
            from_info = reply.get("from", {})
            comment = PostComments.objects.get(comment_id=reply["parent"]["id"])
            CommentReplies.objects.update_or_create(
                comment=comment,
                reply_id=reply["id"],
                defaults={
                    "date": reply["created_time"],
                    "author": from_info.get("name", ""),
                    "fields": {
                        "from": from_info,
                        "like_count": reply.get("like_count", 0),
                    },
                    "message": reply.get("message", ""),
                },
            )

    def sync_comments(self, params={"initial_sync": False}):
        print("sync comments")
        account = Account.objects.get(page_id=self.page_id, user_id=self.user_id)
        posts = AccountObject.objects.filter(account=account)
        batch = []

        for post in posts:
            batch.append(
                {
                    "method": "GET",
                    "relative_url": f"{post.object_id}/comments?fields=comment_count,like_count,message,from,created_time",
                }
            )
        comments = self.fetch_bulk_data(self.user_id, self.page_id, batch)
        reply_batch = []
        for comment in comments:
            post = AccountObject.objects.get(
                object_id__contains=comment["id"].split("_")[0],
                account=account,
            )
            from_info = comment.get("from", {})
            print(f"sync comments for {post.id}")
            _comment, c = PostComments.objects.update_or_create(
                object_id=post.id,
                comment_id=comment["id"],
                defaults={
                    "date": comment["created_time"],
                    "author": from_info.get("name", ""),
                    "fields": {
                        "from": from_info,
                        "comment_count": comment.get("comment_count", 0),
                        "like_count": comment.get("like_count", 0),
                    },
                    "message": comment.get("message", ""),
                },
            )
            reply_batch.append(
                {
                    "method": "GET",
                    "relative_url": f"{_comment.comment_id}/comments?fields=like_count,message,from,created_time,parent",
                }
            )
            # sync replies for every comments
            #self.save_replies(_comment)
        self.bulk_save_replies(reply_batch)


        # for post in posts:
        #     url = f"{post.object_id}/comments?fields=comment_count,like_count,message,from,created_time"
        #     output = self.fetch_graph_data(self.user_id, self.page_id, url)
        #     for comment in output:
        #         from_info = comment.get("from", {})
        #         _comment, c = PostComments.objects.update_or_create(
        #             object_id=post.id,
        #             comment_id=comment["id"],
        #             defaults={
        #                 "date": comment["created_time"],
        #                 "author": from_info.get("name", ""),
        #                 "fields": {
        #                     "from": from_info,
        #                     "comment_count": comment.get("comment_count", 0),
        #                     "like_count": comment.get("like_count", 0),
        #                 },
        #                 "message": comment.get("message", ""),
        #             },
        #         )
        #         # sync replies for every comments
        #         self.save_replies(_comment)

    def fetch_fb_messages(self, params={"initial_sync": False}):
        url = "me/conversations?fields=messages{message,from,attachments,created_time},updated_time,message_count"  # noqa E501
        if params["initial_sync"]:
            url = url + "&since=" + settings.SYNC_SINCE
        else:
            if "since" in params:
                url = url + "&since=" + params["since"]
            if "until" in params:
                url = url + "&until=" + params["until"]

        output = self.fetch_graph_data(self.user_id, self.page_id, url)
        return output
        # batch = [{"method": "GET", "relative_url": url}]
        # batch_response = self.get_graph_api(
        #     user_id=self.user_id, page_id=self.page_id
        # ).put_object(parent_object="/", connection_name="", batch=json.dumps(batch))
        # # print(batch_response)
        # response = batch_response[0]
        # body = json.loads(response["body"])
        # return body["data"]

    def sync_message(self, params={"initial_sync": False}):
        print("sync messages")
        page = Account.objects.get(page_id=self.page_id, user_id=self.user_id)
        messages = self.fetch_fb_messages(params)
        for msg in messages:
            msgs = msg["messages"]["data"]
            for m in msgs:
                AccountInbox.objects.get_or_create(
                    account=page,
                    author=m["from"]["name"],
                    date=m["created_time"],
                    defaults={"message": m["message"], "fields": {"from": m["from"]}},
                )
