from webapp.apps.linkedin.models import PageStats, PageStatsByDay
from rest_framework import serializers


class PageAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PageStats
        fields = [
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
            "page",
        ]


class PageAnalyticsByDay(serializers.ModelSerializer):
    date = serializers.DateField(source="stats_date")

    class Meta:
        model = PageStatsByDay
        fields = [
            "page",
            "shareCount",
            "clickCount",
            "engagement",
            "likeCount",
            "impressionCount",
            "commentCount",
            "date"
        ]
