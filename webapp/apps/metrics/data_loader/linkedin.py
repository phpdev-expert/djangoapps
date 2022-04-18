import requests
from django.conf import settings
from urllib.parse import quote
import time
import calendar
from datetime import datetime, timedelta

from webapp.apps.metrics.models import Account, AccountMetrics, AccountObject
from webapp.apps.metrics.data_loader import InputDataLoader
from webapp.base.exceptions import LinkedinAPIRevokedException
import logging

log = logging.getLogger("linkedin")


class LinkedinDataLoader(InputDataLoader):
    def __init__(self, user_id, page_id):
        self.user_id = user_id
        self.page_id = page_id

    def get_page_urn(self, page_id):
        """
        to get page urn from page_id
        :param page_id:
        :return:
        """
        return f"urn:li:organization:{page_id}"

    def api_connect(self, url, access_token, data=None, params=None):
        """
        Cpnnect to Linkedin Api
        :param url:
        :param access_token:
        :param data:
        :param params:
        :return:
        """
        URL = settings.LINKEDIN_BASE_URL + url
        headers = {
            "Authorization": f"Bearer {access_token}",
            # "cache-control": "no-cache",
            "X-Restli-Protocol-Version": "2.0.0",
        }

        if data:
            response = requests.post(url=URL, headers=headers, data=data)
        if params:
            response = requests.get(url=URL, headers=headers, params=params)
        else:
            response = requests.request("get", url=URL, headers=headers)

        if response.status_code != 200:
            error = response.json()
            if error["status"] == 401:
                raise LinkedinAPIRevokedException(error["message"])
            else:
                raise Exception(error["message"])

        return response

    def get_page_post_ids(self, page):
        """
        to receive post ids of a page
        :param page:
        :return:
        """
        posts = AccountObject.objects.filter(account=page, object_type="post").all()
        post_ids = {}
        for m in posts:
            post_ids[m.object_id] = m.id
        return post_ids

    def save_page(self, data):
        page, c = Account.objects.get_or_create(
            type="linkedin", page_id=self.page_id, user_id=self.user_id
        )
        data_dict = {}
        page.name = data.get("name")
        page.status = data.get("status")
        page.token = data.get("access_token")
        if data.get("picture_url"):
            data_dict.update({"profile_pic_url": data.get("picture_url")})
            page.data = data_dict
        now = datetime.now()
        page.last_synced = now.strftime("%Y-%m-%d %H:%M:%S")
        page.save()
        return c

    def fetch_insights(self):
        page = Account.objects.get(page_id=self.page_id, user_id=self.user_id)
        try:
            self.fetch_and_save_page_analytics()
        except Exception as err:
            update = ["sync_status", "error"]
            if isinstance(err, LinkedinAPIRevokedException):
                page.status = "revoked"
                update.append("status")
            self.flag = False
            page.sync_status = "failed"
            page.error = str(err)
            page.save(update_fields=update)

        try:
            self.fetch_and_save_page_analytics(period="day")
        except Exception as err:
            import traceback
            traceback.print_exc()
            self.flag = False
            page.sync_status = "failed"
            page.error = str(err)
            page.save()
        # if self.flag:
        #     page.sync_status = "ok"
        #     page.error = ""
        #     page.save()

        # self.fetch_and_save_post()
        return page

    def fetch_and_save_page_analytics(self, period="lifetime"):
        page = self.get_page(user_id=self.user_id, page_id=self.page_id)
        if period == "day":
            # dt = datetime.utcnow()
            # end = dt.timestamp() * 1000.0
            if page:
                day = page.accountmetrics_set.filter(
                    object_id=None, date__isnull=False
                ).last()
                if day:
                    dt_obj = datetime.strptime(
                        str(day.date)[:10], "%Y-%m-%d"
                    ) + timedelta(days=1)
                    start = calendar.timegm(dt_obj.utctimetuple()) * 1000
                else:
                    # start = 1546300800000  # According to 1st Jan 2019
                    # start = 1583020800000
                    dt_obj = datetime.strptime(settings.SYNC_SINCE, "%Y-%m-%d")
                    # for last year
                    start = calendar.timegm(dt_obj.utctimetuple()) * 1000
                end = dt_obj + timedelta(days=420)
                end = calendar.timegm(end.utctimetuple()) * 1000
                url = (
                    "/v2/organizationalEntityShareStatistics?q=organizationalEntity"
                    f"&organizationalEntity={quote(self.get_page_urn(page.page_id))}&"
                    f"timeIntervals=(timeRange:(start:{start},end:{end}),timeGranularityType:DAY)"
                )
                resp = self.api_connect(access_token=page.token, url=url)
        else:
            url = "/v2/organizationalEntityShareStatistics"
            params = {
                "q": "organizationalEntity",
                "organizationalEntity": self.get_page_urn(page.page_id),
            }
            resp = self.api_connect(access_token=page.token, url=url, params=params)

        if resp.status_code == 200:
            response = resp.json()
            response = response["elements"]
            metrics = self.get_metrics(type="linkedin")
            create_objects = []
            update_objects = []
            for resp in response:
                date = (
                    time.strftime(
                        "%Y-%m-%d", time.gmtime(int(resp["timeRange"]["start"]) / 1000)
                    )
                    if period == "day"
                    else None
                )
                for metric, value in resp["totalShareStatistics"].items():
                    if metric in metrics.keys():
                        try:
                            o = AccountMetrics.objects.get(
                                account=page,
                                metrics_id=metrics[metric],
                                object_id=None,
                                date=date,
                            )
                            o.value = value
                            update_objects.append(o)
                        except:  # noqa E722
                            create_objects.append(
                                AccountMetrics(
                                    account=page,
                                    metrics_id=metrics[metric],
                                    value_type=type(value).__name__,
                                    value=value,
                                    date=date,
                                )
                            )
            if period == "day":
                self.fetch_page_follower(page, start, end)
            else:
                self.fetch_page_follower(page)

            AccountMetrics.objects.bulk_create(create_objects)
            AccountMetrics.objects.bulk_update(update_objects, ["value"])
            if period == "day":
                if start != end:
                    self.fetch_and_save_page_analytics(period=period)
        else:
            raise Exception(resp.json())

    def fetch_page_follower(self, page, start=None, end=None):
        metrics = self.get_metrics(type="linkedin")

        if start and end:
            url = (
                "/v2/organizationalEntityFollowerStatistics?q=organizationalEntity"
                f"&organizationalEntity={quote(self.get_page_urn(page.page_id))}&"
                f"timeIntervals=(timeRange:(start:{start},end:{end}),timeGranularityType:DAY)"
            )
            response = self.api_connect(access_token=page.token, url=url)
        else:
            url = "/v2/organizationalEntityFollowerStatistics"
            params = {
                "q": "organizationalEntity",
                "organizationalEntity": self.get_page_urn(page.page_id),
            }
            response = self.api_connect(access_token=page.token, url=url, params=params)
        response = response.json()
        followers_count = 0
        create_objects = []
        update_objects = []

        for resp in response["elements"]:
            followers_count = 0
            if start and end:
                followers_count += resp["followerGains"]["organicFollowerGain"]
                followers_count += resp["followerGains"]["paidFollowerGain"]
            else:
                for follower in resp["followerCountsByAssociationType"]:
                    followers_count += follower["followerCounts"][
                        "organicFollowerCount"
                    ]
                    followers_count += follower["followerCounts"]["paidFollowerCount"]
            date = (
                time.strftime(
                    "%Y-%m-%d", time.gmtime(int(resp["timeRange"]["start"]) / 1000)
                )
                if start and end
                else None
            )

            try:
                o = AccountMetrics.objects.get(
                    account=page,
                    metrics_id=metrics["follower"],
                    object_id=None,
                    date=date,
                )
                o.value = followers_count
                update_objects.append(o)
            except:  # noqa E722
                create_objects.append(
                    AccountMetrics(
                        account=page,
                        metrics_id=metrics["follower"],
                        value_type=type(followers_count).__name__,
                        value=followers_count,
                        date=date,
                    )
                )
        AccountMetrics.objects.bulk_create(create_objects)
        AccountMetrics.objects.bulk_update(update_objects, ["value"])
        return followers_count

    def fetch_and_save_post(self, pagination=None):
        page = self.get_page(user_id=self.user_id, page_id=self.page_id)
        if pagination:
            url = pagination
        else:
            url = f"/v2/ugcPosts?q=authors&authors=List({quote(self.get_page_urn(page.page_id))})"
        # if page_url:
        #     url = page_url
        response = self.api_connect(access_token=page.token, url=url)
        response = response.json()

        # To get share urn of post activity
        shares = list()
        create_objects = []
        update_objects = []
        for activity in response["elements"]:
            # activities.append(activity)
            try:
                o = AccountObject.objects.get(
                    account=page, object_id=activity["id"], object_type="post"
                )
                o.description = activity["specificContent"][
                    "com.linkedin.ugc.ShareContent"
                ]["shareCommentary"]["text"]
                update_objects.append(o)
            except:  # noqa E722
                media = []
                for m in activity["specificContent"]["com.linkedin.ugc.ShareContent"][
                    "media"
                ]:
                    media.append(m.get("originalUrl"))
                create_objects.append(
                    AccountObject(
                        account=page,
                        object_id=activity["id"],
                        object_type="post",
                        title=activity["specificContent"][
                            "com.linkedin.ugc.ShareContent"
                        ]["shareCommentary"]["text"],
                        data={"media": media},
                        date_posted=time.strftime(
                            "%Y-%m-%d %H:%M:%S",
                            time.gmtime(int(activity["firstPublishedAt"]) / 1000.0),
                        ),
                    )
                )

            shares.append(activity["id"])
        AccountObject.objects.bulk_create(create_objects)
        AccountObject.objects.bulk_update(update_objects, ["description"])
        self.fetch_and_save_post_analytics(page=page, shares=shares)
        return response

    def fetch_and_save_post_analytics(self, page, shares):
        share_urn = ",".join([quote(str(elem)) for elem in shares])
        url = (
            "/v2/organizationalEntityShareStatistics?q=organizationalEntity"
            f"&organizationalEntity={quote(self.get_page_urn(page.page_id))}&"
            f"shares=List({share_urn})"
        )
        response = self.api_connect(access_token=page.token, url=url)
        response = response.json()["elements"]
        metrics = self.get_metrics(type="linkedin")
        posts = self.get_page_post_ids(page)
        create_objects = []
        update_objects = []
        for resp in response:
            object = posts[resp["share"]] if resp["share"] in posts.keys() else None
            for metric, value in resp["totalShareStatistics"].items():
                try:
                    o = AccountMetrics.objects.get(
                        account=page,
                        metrics_id=metrics[metric],
                        object_id_id=object,
                        date=None,
                    )
                    o.value = value
                    update_objects.append(o)
                except:  # noqa E722
                    create_objects.append(
                        AccountMetrics(
                            account=page,
                            metrics_id=metrics[metric],
                            value_type=type(value).__name__,
                            value=value,
                            object_id_id=object,
                        )
                    )
        AccountMetrics.objects.bulk_create(create_objects)
        AccountMetrics.objects.bulk_update(update_objects, ["value"])
