from datetime import datetime
import time

from webapp.apps.linkedin.serializers.linkedin_account_serializer import PageSerializer
from webapp.apps.linkedin.serializers.page_analytics_serializer import PageAnalyticsSerializer, PageAnalyticsByDay
from webapp.apps.linkedin.models import PageStats


def get_page_by_urn(urn):
    try:
        return PageStats.objects.get(page_urn=urn)
    except Exception:
        return None


def save_page_analytics(page, stats, followers):
    stats = stats['totalShareStatistics']
    follower_count = 0
    stats["page"] = page.id
    for follower in followers:
        follower_count += follower["followerCounts"]["organicFollowerCount"]
        follower_count += follower["followerCounts"]["paidFollowerCount"]
    stats['followerCount'] = follower_count
    if page.pagestats_set.exists():
        instance = page.pagestats_set.get()
    else:
        instance = None
    serializer = PageAnalyticsSerializer(data=stats, instance=instance, partial=True)
    if serializer.is_valid(raise_exception=True):
        serializer.save()
    return serializer.data


def save_page_status(instance, sync_status=None, message=None, status=None):
    data = dict()
    if sync_status:
        data["sync_status"] = sync_status
    if message:
        data["message"] = message
    if status:
        data["status"] = status
    now = datetime.now()
    data["last_sync_time"] = now.strftime('%Y-%m-%d %H:%M:%S')
    serializer = PageSerializer(instance=instance, partial=True, data=data)
    if serializer.is_valid(raise_exception=True):
        serializer.save()


def save_page_analytics_by_date(page, analytics):
    analytics = analytics["elements"]
    for analytic in analytics:

        data = analytic["totalShareStatistics"]
        data["date"] = time.strftime('%Y-%m-%d', time.gmtime(int(analytic["timeRange"]["start"]) / 1000))
        data["page"] = page.id
        serializer = PageAnalyticsByDay(instance=None, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
