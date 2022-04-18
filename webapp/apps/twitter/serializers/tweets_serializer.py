from webapp.apps.twitter.models import Tweets
from drf_writable_nested import WritableNestedModelSerializer


class TweetsSerializer(WritableNestedModelSerializer):
    class Meta:
        model = Tweets
        fields = [
            'tweet_id',
            'tweet_date',
            'text',
            'media_url',
            'retweet_count',
            'favourite_count',
            "is_quote_status",
            "retweeted",
            "user"
        ]