from webapp.apps.linkedin.models import PostStats
from rest_framework import serializers


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostStats
        fields = [
            "urn",
            "text",
            "post_date"
        ]


class PostAnalyticSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostStats
        fields = [
            "urn",
            "shareCount",
            "clickCount",
            "engagement",
            "likeCount",
            "impressionCount",
            "commentCount"
        ]


class PostTableSerializer(serializers.ModelSerializer):
    page = serializers.SerializerMethodField()

    class Meta:
        model = PostStats
        fields = [
            "urn",
            "page",
            "text",
            "post_date",
            "shareCount",
            "clickCount",
            "engagement",
            "likeCount",
            "impressionCount",
            "commentCount"
        ]

    def get_page(self, obj):
        return obj.page.name
