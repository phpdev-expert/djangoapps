from webapp.apps.twitter.models import Tweets, TweetReply, TwitterAccount
from rest_framework import serializers


class RecursiveField(serializers.Serializer):
    def to_representation(self, value):
        data = dict()
        data["reply_id"] = value.reply_id
        data["reply_date"] = value.reply_date
        serializer = self.parent.parent.__class__(value, context=self.context)
        data.update(serializer.data)
        data.pop("tweet_id")
        data.pop("tweet_date")
        return data


class TweetReplySerializer(serializers.ModelSerializer):
    # replies = RecursiveField(source="parent", many=True)
    replies_count = serializers.SerializerMethodField(default=0)

    class Meta:
        model = TweetReply
        fields = [
            "user",
            "reply_id",
            "reply_date",
            "text",
            "media_url",
            "retweet_count",
            "favourite_count",
            "replies_count",
            # "replies"
        ]

    def get_replies_count(self, obj):
        replies = obj.tweetreply_set.count()
        return replies


class TweetWithReplySerializer(serializers.ModelSerializer):
    replies_count = serializers.SerializerMethodField(default=0)
    replies = RecursiveField(source="tweetreply_set", many=True)

    class Meta:
        model = Tweets
        fields = [
            "tweet_id",
            "tweet_date",
            "text",
            "media_url",
            "retweet_count",
            "favourite_count",
            "replies_count",
            "replies"
        ]

    def get_replies_count(self, obj):
        replies = obj.tweetreply_set.count()
        return replies


class TweetSerializer(serializers.ModelSerializer):
    replies_count = serializers.SerializerMethodField(default=0)

    class Meta:
        model = Tweets
        fields = [

            "user",
            "tweet_id",
            "tweet_date",
            "text",
            "media_url",
            "retweet_count",
            "favourite_count",
            "replies_count",
        ]

    def get_replies_count(self, obj):
        replies = obj.tweetreply_set.count()
        return replies


class TweetsTableSerializer(serializers.Serializer):

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if isinstance(instance, Tweets):
            serializer = TweetSerializer(instance)
            serializer_data = serializer.data
            data["screen_name"] = instance.user.screen_name
            data["date"] = serializer_data["tweet_date"]
            data["message"] = serializer_data["text"]
            data["retweet_count"] = serializer_data["retweet_count"]
            data["favourite_count"] = serializer_data["favourite_count"]
            data["replies_count"] = serializer_data["replies_count"]

        if isinstance(instance, TweetReply):
            serializer = TweetReplySerializer(instance)
            serializer_data = serializer.data
            data["screen_name"] = instance.user.screen_name
            data["date"] = serializer_data["reply_date"]
            data["message"] = serializer_data["text"]
            data["retweet_count"] = serializer_data["retweet_count"]
            data["favourite_count"] = serializer_data["favourite_count"]
            data["replies_count"] = serializer_data["replies_count"]
        return data