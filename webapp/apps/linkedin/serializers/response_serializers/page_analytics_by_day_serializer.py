from webapp.apps.linkedin.models import PageStats, PageStatsByDay, Page
from rest_framework import serializers


class PageAnalyticsByDayResponse(serializers.ModelSerializer):
    date = serializers.DateField(source="stats_date")
    postCount = serializers.SerializerMethodField()

    class Meta:
        model = PageStatsByDay
        fields = [
            "shareCount",
            "clickCount",
            "engagement",
            "likeCount",
            "impressionCount",
            "commentCount",
            "date",
            "postCount"
        ]

    def get_postCount(self, obj):
        return obj.page.poststats_set.filter(post_date__date=obj.stats_date).count()


class FilterPageAnalytics(serializers.ModelSerializer):
    analytic = PageAnalyticsByDayResponse(source="pagestatsbyday_set", many=True)

    class Meta:
        model = Page
        fields = [
            "name",
            "analytic"
        ]