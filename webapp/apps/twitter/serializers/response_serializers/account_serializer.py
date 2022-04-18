from webapp.apps.twitter.models import TwitterAccount, DirectMessages, Mention
from rest_framework import serializers
from django.db.models import Q


class TwitterAccountSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="screen_name")
    dm_count = serializers.SerializerMethodField()
    mentions_count = serializers.SerializerMethodField()
    tweet_count = serializers.SerializerMethodField()

    class Meta:
        model = TwitterAccount
        fields = [
            "twitter_id",
            "name",
            "location",
            "language",
            "followers_count",
            "friends_count",
            "favourites_count",
            "dm_count",
            "mentions_count",
            "tweet_count"
        ]

    def get_dm_count(self, obj):
        try:
            messages = DirectMessages.objects.filter(receiver_id=obj.twitter_id).count()
        except Exception:
            messages = None

        return messages

    def get_mentions_count(self, obj):
        try:
            mentions = Mention.objects.filter(Q(twitter_id=obj.twitter_id) & (Q(reply__user__id=obj.id) | Q(reply__tweet_id__user__id=obj.id) | Q(tweet__user__id=obj.id))).count()
            mentions = mentions + Mention.objects.filter(Q(twitter_id=obj.twitter_id) & (Q(reply__user__id=None) & Q(reply__tweet_id__user__id=None)) & (Q(tweet__user__id=None))).count()
        except Exception:
            mentions = 0

        return mentions

    def get_tweet_count(self, obj):
        tweets = obj.tweets_set.count()
        return tweets


class TwitterAccountListSerializer(serializers.ModelSerializer):
    class Meta:
        model = TwitterAccount
        fields = [
            "twitter_id",
            "screen_name",
        ]