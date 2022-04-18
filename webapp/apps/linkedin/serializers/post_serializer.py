from webapp.apps.linkedin.models import PostStats
from rest_framework import serializers


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostStats
        fields = [
            "page",
            "urn",
            "text",
            "post_date",
            "media"
        ]


class PostStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostStats
        fields = [
            "page",
            "urn",
            "shareCount",
            "clickCount",
            "engagement",
            "likeCount",
            "impressionCount",
            "commentCount"
        ]