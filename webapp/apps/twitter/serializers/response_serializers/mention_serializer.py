from rest_framework import serializers

from webapp.apps.twitter.models import Mention, Tweets
from webapp.apps.twitter.serializers.response_serializers.tweet_serializer import TweetSerializer, TweetReplySerializer


class MentionSerializer(serializers.ModelSerializer):
    type = serializers.CharField(default="Mention")
    date = serializers.CharField(source="mention_date")
    class Meta:
        model = Mention
        fields = [
            "type",
            "date",
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["language"] = ""
        representation["country"] = ""
        if instance.tweet:
            message = instance.tweet.text
            representation["language"] = instance.tweet.language
            representation["country"] = instance.tweet.location
            representation["author"] = instance.tweet.user.screen_name
        if instance.reply:
            message = instance.reply.text
            representation["language"] = instance.reply.language
            representation["country"] = instance.reply.location
            representation["author"] = instance.reply.user.screen_name
        representation["message"] = message


        return representation