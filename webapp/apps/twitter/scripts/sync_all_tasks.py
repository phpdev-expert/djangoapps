from webapp.apps.twitter.services.twitter_account import get_twitter_acc_by_id
from webapp.apps.twitter.tasks import sync_account, sync_direct_message, sync_tweets, sync_tweet_reply
from webapp.apps.twitter.models import TwitterAccount
from datetime import datetime
from webapp.apps.twitter.serializers.twitter_account_serializer import SyncAccountInfoSerializer


def sync_all(access_token_secret, twitter_id, access_token, auth_id=None):
    data = dict()
    try:
        # Sync User
        sync_account(twitter_id=twitter_id,access_token_secret=access_token_secret, access_token=access_token, auth_id=auth_id)
        # Sync direct messages
        sync_direct_message(access_token_secret=access_token_secret, access_token=access_token, twitter_id=twitter_id)
        # sync tweets
        sync_tweets(twitter_id=twitter_id,access_token_secret=access_token_secret, access_token=access_token)

        # sync tweet reply
        sync_tweet_reply(twitter_id=twitter_id, access_token_secret=access_token_secret, access_token=access_token)
        data['status'] = TwitterAccount.OK
        data['message'] = "Sync Success"
    except Exception as exc:
        data['status'] = TwitterAccount.FAILED
        data['message'] = str(exc)
    now = datetime.now()
    data['last_sync_time'] = now.strftime('%Y-%m-%d %H:%M:%S')
    instance = get_twitter_acc_by_id(twitter_id)
    serializer = SyncAccountInfoSerializer(instance=instance, data=data)
    serializer.is_valid(raise_exception=True)
    serializer.save()


