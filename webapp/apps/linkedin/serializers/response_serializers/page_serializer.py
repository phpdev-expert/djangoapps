from webapp.apps.linkedin.models import PageStats, Page
from rest_framework import serializers
from webapp.base.api_init import api_connect


class PageSerializer(serializers.ModelSerializer):
    postCount = serializers.SerializerMethodField()
    page = serializers.IntegerField(source="page.page_id")
    name = serializers.CharField(source="page.name")

    class Meta:
        model = PageStats
        fields = [
            "page",
            "name",
            "shareCount",
            "uniqueImpressionsCount",
            "clickCount",
            "engagement",
            "shareMentionsCount",
            "likeCount",
            "impressionCount",
            "commentMentionsCount",
            "commentCount",
            "followerCount",
            "postCount"
        ]

    def get_postCount(self, obj):
        return obj.page.poststats_set.count()


class PageListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Page
        fields = [
            "page_id",
            "name",
            "phone",
            "website",
            "about",
            "description",
            "cover_url",
            "picture_url",
        ]
