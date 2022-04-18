import time

from webapp.apps.linkedin.services.page_analytics_services import get_page_by_urn
from webapp.apps.linkedin.serializers.post_serializer import PostStatsSerializer, PostSerializer
from webapp.apps.linkedin.models import PostStats


def get_post_by_urn(urn):
    try:
        return PostStats.objects.get(urn=urn)
    except Exception:
        return None


def save_page_post(activities, page):
    data = dict()
    data["page"] = page.id

    for activity in activities:
        media = []
        if len(activity["specificContent"]["com.linkedin.ugc.ShareContent"]["media"]) > 0:
            for url in activity["specificContent"]["com.linkedin.ugc.ShareContent"]["media"]:
                for media_url in url["thumbnails"]:
                    media.append(media_url["url"])
        share = get_post_by_urn(activity['id'])
        data["urn"] = activity['id']
        data["text"] = activity["specificContent"]["com.linkedin.ugc.ShareContent"]["shareCommentary"]["text"]
        data["media"] = media
        data["post_date"] = time.strftime('%Y-%m-%d %H:%M:%S',
                                          time.gmtime(int(activity["firstPublishedAt"]) / 1000.))

        serializer = PostSerializer(instance=share, data=data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()


def save_page_post_analytics(shares):
    for share in shares:
        get_page = get_post_by_urn(share['share'])
        serializer = PostStatsSerializer(instance=get_page,data=share['totalShareStatistics'], partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
