import calendar
import time
from datetime import datetime, timedelta
from urllib.parse import quote

from celery import shared_task
from django.conf import settings

from webapp.apps.linkedin.serializers.linkedin_account_serializer import PageSerializer, get_page_by_id_and_user_id
from webapp.apps.linkedin.serializers.response_serializers.page_serializer import PageListSerializer
from webapp.apps.linkedin.services.page_analytics_services import save_page_analytics, save_page_status, \
    save_page_analytics_by_date
from webapp.apps.linkedin.services.page_post_service import save_page_post_analytics, save_page_post
from webapp.base import constants
from webapp.base.api_init import api_connect


@shared_task(bind=True, name=settings.LINKEDIN_PAGE_SYNC_TASK, max_retries=1)
def linkedin_saved_task(self, data=None):
    print("Data", data)
    if data:
        status = data.get("status")
        if status == "active":
            page = get_page_by_id_and_user_id(id=data.get("page_id"), user_id=str(data.get("auth_user_id")))
            data["user_id"] = str(data["auth_user_id"])
            serializer = PageSerializer(instance=page, data=data, partial=True)
            if serializer.is_valid(raise_exception=True):
                instance = serializer.save()
                sync_page = get_page_analytics.delay(instance.page_id, data["user_id"])


@shared_task(bind=True, name=settings.SYNC_PAGE_ANALYTICS)
def get_page_analytics(self, page_id, user_id):
    page = get_page_by_id_and_user_id(page_id, user_id)
    url = "/v2/organizationalEntityShareStatistics"
    params = {
        "q": "organizationalEntity",
        "organizationalEntity": page.get_page_urn()
    }
    resp = api_connect(access_token=page.access_token, url=url, params=params)
    if resp.status_code == 200:
        try:
            response = resp.json()
            follower = get_page_follower(access_token=page.access_token, urn=page.get_page_urn())
            save_page_analytics(stats=response['elements'][0], page=page, followers=follower['elements'][0]['followerCountsByAssociationType'])
            get_page_analytics_by_date(page=page, start=1546300800000, end=time.time() * 1000.0)
            get_shares.delay(page_id, user_id)
            # save_page_status(instance=page, status=constants.OK, message="SYNC Success")

        except Exception as exc:
            save_page_status(instance=page, sync_status=constants.FAILED, message=str(exc), status="active")
    else:
        resp = resp.json()
        save_page_status(instance=page, status="revoked", sync_status=constants.FAILED, message=resp.get("message"))
        data = PageSerializer(instance=page).data
        data["social_account"] = data.pop("user_id")
        linkedin_saved_task.delay(data=data)


def save_page_details(access_token, urn):
    urn = urn.replace("urn:li:organization:","")
    url = f"/v2/organizations/{urn}"
    params = {
        "projection": "(vanityName)"
    }
    try:
        response = api_connect(access_token=access_token, url=url, params=params)
        return response["vanityName"]
    except Exception:
        return None


def get_page_analytics_by_date(page, start=None, end=None):

    dt = datetime.utcnow()
    end = dt.timestamp() * 1000.0
    if page:
        day = page.pagestatsbyday_set.last()
        if day:
            dt_obj = datetime.strptime(str(day.stats_date),
                                       '%Y-%m-%d') + timedelta(days=1)
            start = calendar.timegm(dt_obj.utctimetuple()) * 1000
        else:
            start = 1546300800000  # According to 1st Jan 2019
        url = f"/v2/organizationalEntityShareStatistics?q=organizationalEntity&organizationalEntity={quote(page.get_page_urn())}&timeIntervals=(timeRange:(start:{start},end:{end}),timeGranularityType:DAY)"
        response = api_connect(access_token=page.access_token, url=url)
        response = response.json()

        if "message" not in response.keys():
            save_page_analytics_by_date(page=page, analytics=response)



# @shared_task
def get_post_analytics(access_token, shares, page_urn):
    share_urn = ','.join([quote(str(elem)) for elem in shares])
    # for i, share in enumerate(shares):
    #     share_urn + quote(share) + ","
    url = f"/v2/organizationalEntityShareStatistics?q=organizationalEntity&organizationalEntity={quote(page_urn)}&shares=List({share_urn})"

    params = {
        "q": "organizationalEntity",
        "organizationalEntity": quote(page_urn),
        "shares": f"List({share_urn})"
    }

    response = api_connect(access_token=access_token, url=url)
    response = response.json()
    save_page_post_analytics(shares=response["elements"])
    return response


# @shared_task
def get_page_follower(urn, access_token,start=None, end=None):
    url = "/v2/organizationalEntityFollowerStatistics"
    params = {
        "q": "organizationalEntity",
        "organizationalEntity": urn
    }
    if start and end:
        params["timeIntervals.timeRange.start"] = start
        params["timeIntervals.timeRange.end"] = end
        params["timeIntervals.timeGranularityType"] = "DAY"
    response = api_connect(access_token=access_token, url=url, params=params)
    return response.json()

#
# @shared_task
# def get_post():
#     url = "v2/ugcPosts"
#     params = {
#         "q": "authors",
#         "authors": "urn:li:organization:13406193"
#     }
#     response = api_connect(access_token=ACCESS_TOKEN, url=url, params=params)
#     print(response)


@shared_task(bind=True, name=settings.LINKEDIN_SYNC_POST_ANALYTICS)
def get_shares(self, page_id, user_id, page_url=None):
    page = get_page_by_id_and_user_id(page_id, user_id)
    urn = page.get_page_urn()
    try:
        # To get List of activities of organisation
        url = f"/v2/ugcPosts?q=authors&authors=List({quote(urn)})"
        if page_url:
            url = page_url
        response = api_connect(access_token=page.access_token, url=url)
        response = response.json()
        activities = list()

        # To get share urn of post activity
        shares = list()
        for activity in response['elements']:
            activities.append(activity)
            shares.append(activity['id'])
        # print("activities", activities)

        # save new post
        save_page_post(activities=activities, page=page)

        # Fetch Post analytics
        get_post_analytics(access_token=page.access_token, shares=shares, page_urn=page.get_page_urn())
        if len(response["paging"]["links"]) > 0:
            for paging in response["paging"]["links"]:
                if "rel" in paging.keys():
                    if paging["rel"] == "next":
                        res = self.delay(page_url=paging["href"], page_id=page_id)
                        while not res.ready():
                            time.sleep(2)
                else:
                    save_page_status(instance=page, sync_status=constants.OK, message="SYNC Success", status="active")
                    serializer = PageListSerializer(instance=page)
                    data = serializer.data
                    data["last_sync_time"] = page.last_sync_time
                    data["auth_user_id"] = page.user_id
                    linkedin_saved_task.delay(data=data)

        else:
            save_page_status(instance=page, sync_status=constants.OK, message="SYNC Success", status="active")
            serializer = PageListSerializer(instance=page)
            data = serializer.data
            data["last_sync_time"] = page.last_sync_time
            data["auth_user_id"] = page.user_id
            linkedin_saved_task.delay(data=data)

    except Exception as exc:
        save_page_status(instance=page, sync_status=constants.FAILED, message=str(exc), status="active")


@shared_task(bind=True, name=settings.LINKEDIN_PAGE_DELETE_TASK)
def delete_linkedin_page(self, data=None):
    if data:
        status = data.get("status")
        if status == "delete":
            page = get_page_by_id_and_user_id(data.get("page_id"), data.get("auth_user_id"))
            if page:
                page.pagestats_set.all().delete()
                page.poststats_set.all().delete()
                page.pagestatsbyday_set.all().delete()
                page.delete()