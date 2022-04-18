from webapp.apps.twitter.models import TweetReply
from drf_writable_nested import WritableNestedModelSerializer


class TweetReplySerializer(WritableNestedModelSerializer):
    class Meta:
        model = TweetReply
        fields = [
            "user",
            'reply_id',
            'twitter_id',
            'tweet_id',
            'text',
            'media_url',
            'reply_date',
            'retweet_count',
            'favourite_count',
            "parent"
        ]