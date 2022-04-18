from webapp.apps.twitter.models import TwitterAccount
from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers


class TwitterAccountSerializer(WritableNestedModelSerializer):
    """
    Twitter account serializer for saving data
    """

    class Meta:
        model = TwitterAccount
        fields = [
            'auth_user_id',
            'twitter_id',
            'access_token',
            'access_token_secret',
            'first_name',
            'last_name',
            'screen_name',
            'location',
            'language',
            'followers_count',
            'friends_count',
            'favourites_count',
            "account_type",
            'status',
            'last_sync_time',
            'sync_status',
            'message',
        ]


class SyncAccountInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TwitterAccount
        fields = [
            'last_sync_time',
            'sync_status',
            'message',
            'status'
        ]