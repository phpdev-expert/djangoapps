from datetime import datetime, timedelta
from django.conf import settings
from django.db.models import Q

from webapp.apps.linkedin import GraphAPIError
from webapp.apps.metrics.models import (
    Account,
    AccountMetrics,
    Metrics,
    AccountObject,
    PostComments,
    CommentReplies,
)
from webapp.apps.metrics.data_loader import InputDataLoader
import logging

log = logging.getLogger("instagram")


class InstagramDataLoader(InputDataLoader):
    def __init__(self, user_id, page_id):
        self.user_id = user_id
        self.page_id = page_id

    def fetch_initial_syc(self, url):
        since = settings.SYNC_SINCE
        until = (datetime.strptime(since, "%Y-%m-%d") + timedelta(days=30)).strftime(
            "%Y-%m-%d"
        )
        repeat_to_fetch = True
        data = []
        while repeat_to_fetch:
            if datetime.strptime(since, "%Y-%m-%d") >= datetime.today():
                break
            if datetime.strptime(until, "%Y-%m-%d") > datetime.today():
                until = datetime.today().strftime("%Y-%m-%d")
                repeat_to_fetch = False
            date_formatted_url = url + "&since={}&until={}".format(since, until)
            print(date_formatted_url)
            data += self.fetch_graph_data(
                self.user_id, self.page_id, date_formatted_url
            )
            since = (datetime.strptime(until, "%Y-%m-%d") + timedelta(days=1)).strftime(
                "%Y-%m-%d"
            )
            until = (
                datetime.strptime(since, "%Y-%m-%d") + timedelta(days=30)
            ).strftime("%Y-%m-%d")
        return data

    def save_page(self, data):
        page, created = Account.objects.get_or_create(
            type="instagram", page_id=self.page_id, user_id=self.user_id
        )
        data_dict = {}
        if data.get("screen_name"):
            page.name = data.get("screen_name")
        if data.get("status"):
            page.status = data.get("status")
        if data.get("access_token"):
            page.token = data.get("access_token")
        if data.get("picture_url"):
            data_dict.update({"profile_pic_url": data.get("picture_url")})
            page.data = data_dict
        if data.get("account_type"):
            data_dict.update({"account_type": data.get("account_type")})
            page.data = data_dict
        page.save()
        return created

    def fetch_insta_metrics(
        self, graph_id, metrics, params={"period": "day", "initial_sync": False}
    ):
        day_metrics = ""
        for metric in metrics:
            day_metrics += f"'{metric}',"

        url = f"{graph_id}/insights/?metric=[{day_metrics}]&period=day"
        extracted_metrics = {}
        if params["initial_sync"]:
            data = self.fetch_initial_syc(url)
        else:
            if "since" in params:
                url = url + "&since=" + params["since"]
            print("url", url)
            data = self.fetch_graph_data(self.user_id, self.page_id, url)
        extracted_metrics = self.prepare_metrics(data, extracted_metrics)
        return extracted_metrics

    def fetch_insights(self, params={"initial_sync": False}):
        log.info(
            "fetching insta metrics . initial_sync : {}".format(params["initial_sync"])
        )
        account = Account.objects.get(page_id=self.page_id, user_id=self.user_id)
        metrics = (
            Metrics.objects.filter(
                Q(platform="instagram")
                # & Q(fields__level="page")
                & Q(fields__is_field=False)
            )
            .exclude(metric__exact="")
            .exclude(metric__exact="null")
        )

        all_metrics = list(metrics.values_list("metric", flat=True))
        metric_ids = {}
        for m in metrics:
            metric_ids[m.metric] = m.id

        try:
            metrics = self.fetch_insta_metrics(self.page_id, all_metrics, params)
        except Exception as ex:
            log.info("Error in insta fetch_insights {}".format(str(ex)))
            update = ["sync_status", "error"]
            if isinstance(ex, GraphAPIError):
                account.status = "revoked"
                update.append("status")
            self.flag = False
            account.sync_status = "failed"
            account.error = str(ex)
            account.save(update_fields=update)
            # log.info(ex)
        else:
            create_objects = []
            update_objects = []
            log.info("got metrics : {}".format(len(metrics)))
            for metric, records in metrics.items():
                for period, values in records.items():
                    for row in values:
                        if period == "lifetime":
                            date = None
                        if period == "day":
                            date = row["end_time"]
                        try:

                            o = AccountMetrics.objects.get(
                                account=account,
                                metrics_id=metric_ids[metric],
                                date=date,
                            )
                            o.value = row["value"]
                            update_objects.append(o)
                        except:  # noqa E722
                            create_objects.append(
                                AccountMetrics(
                                    account=account,
                                    metrics_id=metric_ids[metric],
                                    date=date,
                                    value_type=type(row["value"]).__name__,
                                    value=row["value"],
                                )
                            )

            AccountMetrics.objects.bulk_create(create_objects)
            AccountMetrics.objects.bulk_update(update_objects, ["value"])
            # if self.flag:
            #     account.error = ""
            #     #account.sync_status = "ok"
            #     account.save()

    def fetch_insta_posts(self, metrics, params):
        output = []
        fields = ""
        for m in metrics:
            if m == "comments":
                pass
                # sync comments seperately
                # fields += "{}{{user,timestamp,id,text,username}},".format(m)
            else:
                fields += "{},".format(m)
        if len(fields) > 0:
            fields = fields[:-1]
            relative_url = "{}/media?fields=permalink,timestamp,username,caption,media_url,{}".format(  # noqa E501
                self.page_id, fields
            )
            log.info(relative_url)
            # if params["initial_sync"]:
            #     output = self.fetch_initial_syc(relative_url)
            #     # relative_url = relative_url + "&since=2020-01-01&until="+datetime.today().strftime("%Y-%m-%d")
            # else:
            output = self.fetch_graph_data(self.user_id, self.page_id, relative_url)
        return output

    def get_post_table(self, post_id, params):
        post = AccountObject.objects.get(
            object_id=post_id, account__user_id=self.user_id
        )
        url = '/{}/insights?metric=["{}", "{}", "{}", "{}", "{}"]'.format(
            post_id,
            "engagement",
            "impressions",
            "reach",
            "saved",
            "video_views" if post.data["media_type"] != "IMAGE" else None,
        )
        url = url.replace(', "None"', "")
        if params["initial_sync"]:
            data = self.fetch_initial_syc(url)
            # url = url + "&since=2020-01-01&until="+datetime.today().strftime("%Y-%m-%d")
        else:
            data = self.fetch_graph_data(self.user_id, self.page_id, url)
        extracted_metrics = {}
        extracted_metrics = self.prepare_metrics(data, extracted_metrics)
        return extracted_metrics

    def sync_post(self, params={"initial_sync": False}):
        log.info(
            "fetching insta posts . initial_sync : {}".format(params["initial_sync"])
        )
        page = Account.objects.get(page_id=self.page_id, user_id=self.user_id)
        metrics = (
            Metrics.objects.filter(
                Q(platform="instagram")
                & Q(fields__level="post")
                & Q(fields__is_field=True)
            )
            .exclude(metric__exact="")
            .exclude(metric__exact="null")
        )
        all_metrics = list(metrics.values_list("metric", flat=True))
        metric_ids = {}
        for m in metrics:
            metric_ids[m.metric] = m.id
        posts = []
        try:
            posts = self.fetch_insta_posts(all_metrics, params)
        except Exception as err:
            log.info("error in getting post , {}".format(str(err)))
            self.flag = False
            page.sync_status = "failed"
            page.error = str(err)
            page.save()
        log.info("got posts , {}".format(len(posts)))
        for p in posts:
            if "timestamp" in p:
                if datetime.strptime(p["timestamp"].split("T",1)[0],"%Y-%m-%d") < datetime.strptime(settings.SYNC_SINCE,"%Y-%m-%d"):
                    break
            post_id = p.get("id")
            media_url = p.get("media_url", None)
            media_type = p.get("media_type", None)
            comments_count = p.get("comments_count", 0)
            like_count = p.get("like_count", 0)
            # print("post", p)
            # print(post_id, p["date_posted"])
            try:
                _post, c = AccountObject.objects.update_or_create(
                    account=page,
                    object_id=post_id,
                    object_type="post",
                    defaults={
                        "title": p.get("caption", ""),
                        "date_posted": p.get("timestamp"),
                    },
                )
                permalink = ""
                permalink = p.get("permalink", "")
                try:
                    permalink = permalink.split("instagram.com/")[1]
                except Exception:
                    pass
                _post.data = {
                    "media_url": media_url,
                    "media_type": media_type,
                    "comments_count": comments_count,
                    "like_count": like_count,
                    "permalink": permalink,
                }
                _post.save()
            except Exception as ex:
                log.info(ex)
                self.flag = False
                page.sync_status = "failed"
                page.error = str(ex)
                page.save()

        # if self.flag:
        #     page.error = ""
        #     page.sync_status = "ok"
        #     page.save()

    def save_replies(self, comment):
        log.info("fetching replies")
        url = f"{comment.comment_id}/replies?fields=like_count,username,text,timestamp"
        replies = self.fetch_graph_data(self.user_id, self.page_id, url)
        for reply in replies:
            CommentReplies.objects.update_or_create(
                comment_id=comment.id,
                reply_id=reply["id"],
                defaults={
                    "date": reply["timestamp"],
                    "author": reply.get("username", 0),
                    "fields": {"like_count": reply.get("like_count", 0)},
                    "message": reply.get("text", ""),
                },
            )

    def sync_comments(self, params={"initial_sync": False}):
        log.info("fetching comments")
        account = Account.objects.get(page_id=self.page_id, user_id=self.user_id)
        posts = AccountObject.objects.filter(account=account)
        for post in posts:
            url = f"{post.object_id}/comments?fields=like_count,username,text,timestamp"
            output = self.fetch_graph_data(self.user_id, self.page_id, url)
            for comment in output:
                _comment, c = PostComments.objects.update_or_create(
                    object_id=post.id,
                    comment_id=comment["id"],
                    defaults={
                        "date": comment["timestamp"],
                        "author": comment.get("username", ""),
                        "fields": {"like_count": comment.get("like_count", 0)},
                        "message": comment.get("text", ""),
                    },
                )
                # sync replies for every comments
                print()
                self.save_replies(_comment)
