from celery import shared_task, Task
import tweepy
from django.conf import settings
from tweepy import TweepError

from webapp.apps.twitter.models import TwitterAccount
from webapp.apps.twitter.serializers.twitter_account_serializer import TwitterAccountSerializer
from webapp.apps.twitter.services.tweet_reply import save_tweet_reply, get_tweet_reply_by_id
from webapp.apps.twitter.services.twitter_account import save_authenticated_user, get_twitter_acc_by_id, \
    get_twitter_acc_by_id_and_user_id, save_twitter_account_status
from webapp.apps.twitter.services.direct_message import save_received_messages
from webapp.apps.twitter.services.tweets import save_tweets, get_tweets_by_twitter_id, get_tweet_by_id, \
    get_tweet_by_id_and_account_id
import json


def connect_api(access_token, access_token_secret):
    auth = tweepy.OAuthHandler(settings.TWITTER_APP_ID, settings.TWITTER_APP_SECRET)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    return api


@shared_task(bind=True, name=settings.TWITTER_ACCOUNT_SYNC_TASK, max_retries=1)
def twitter_saved_task(self, data=None):
    print("Data", data)
    if data:
        status = data.get("status")
        if status == "active":
            social_account_id = str(data.get("social_account_id"))
            auth_user_id = str(data.get("auth_user_id"))
            twitter = get_twitter_acc_by_id_and_user_id(social_account_id, auth_user_id)
            data["twitter_id"] = social_account_id
            serializer = TwitterAccountSerializer(instance=twitter, data=data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                sync_account.delay(social_account_id, auth_user_id)


@shared_task(bind=True, name=settings.SYNC_ACCOUNT)
def sync_account(self, social_account_id, auth_user_id):
    """
    Get Twitter Account From API
    :param access_token_secret:
    :param api:
    :param twitter_id:
    :param access_token:
    :param auth_id:
    :return:
    """
    try:
        twitter = get_twitter_acc_by_id_and_user_id(social_account_id, auth_user_id)
        api = connect_api(twitter.access_token, twitter.access_token_secret)
        user = api.get_user(user_id=social_account_id)
        save_authenticated_user(user, auth_id=auth_user_id)
        sync_direct_message.delay(social_account_id, auth_user_id)
        sync_tweets.delay(social_account_id, auth_user_id)
    except TweepError as err:
        if err.api_code == 89:
            status = "revoked"
            instance = save_twitter_account_status(social_account_id, auth_user_id, status=status, sync_status=TwitterAccount.FAILED, message=err.reason)
            twitter_saved_task.delay(data=TwitterAccountSerializer(instance=instance).data)
    except Exception as msg:
        print("Exception: %s " % msg)
        instance = save_twitter_account_status(social_account_id, auth_user_id,
                                               sync_status=TwitterAccount.FAILED, message=str(msg))
        raise msg


@shared_task(bind=True, name=settings.SYNC_DIRECT_MESSAGE)
def sync_direct_message(self,  social_account_id, auth_user_id):
    try:
        account = get_twitter_acc_by_id_and_user_id(social_account_id, auth_user_id)
        api = connect_api(account.access_token, account.access_token_secret)

        if account:
            messages_list = api.list_direct_messages()
            received = list()
            for message in messages_list:
                # if message.message_create["target"]["recipient_id"] == twitter_id:
                received.append(message.__dict__)
        save_received_messages(messages=received)

    except Exception as msg:
        instance = save_twitter_account_status(social_account_id, auth_user_id,
                                               sync_status=TwitterAccount.FAILED, message=str(msg))
        print("sync message error : {}".format(msg))


@shared_task(bind=True, name=settings.SYNC_TWEETS)
def sync_tweets(self, social_account_id, auth_user_id):
    try:
        account = get_twitter_acc_by_id_and_user_id(social_account_id, auth_user_id)
        if account:
            api = connect_api(account.access_token, account.access_token_secret)
            tweets = api.user_timeline(count=200)
            for tweet in list(tweets):
                save_tweets(tweets=tweet._json, auth_user_id=auth_user_id)

            sync_tweet_reply.delay(social_account_id, auth_user_id)
    except Exception as exc:
        instance = save_twitter_account_status(social_account_id, auth_user_id,
                                               sync_status=TwitterAccount.FAILED, message=str(exc))
        print(exc)


@shared_task(bind=True, name=settings.SYNC_TWEET_REPLY)
def sync_tweet_reply(self, social_account_id, auth_user_id):
    try:
        account = get_twitter_acc_by_id_and_user_id(social_account_id, auth_user_id)
        if account:
            api = connect_api(account.access_token, account.access_token_secret)
            # get_tweets = get_tweets_by_twitter_id(twitter_id)
            timeline = api.mentions_timeline()
            for reply in timeline:
                json = reply._json
                tweet_id = json['in_reply_to_status_id_str']
                tweet = get_tweet_by_id_and_account_id(tweet_id, account.id)

                if tweet_id is not None:
                    save_tweet_reply(json, tweet, auth_user_id)
                else:
                    save_tweets(json, auth_user_id=auth_user_id)
    except Exception as exc:
        instance = save_twitter_account_status(social_account_id, auth_user_id,
                                               sync_status=TwitterAccount.FAILED, message=str(exc))
        print("tasks error : {}".format(exc))