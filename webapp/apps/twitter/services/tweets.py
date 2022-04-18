from webapp.apps.twitter.models import Tweets, Mention
from webapp.apps.twitter.serializers.tweets_serializer import TweetsSerializer
from webapp.apps.twitter.serializers.twitter_account_serializer import TwitterAccountSerializer
from webapp.apps.twitter.services.tweet_reply import save_tweet_reply
from webapp.apps.twitter.services.twitter_account import get_twitter_acc_by_id, get_twitter_acc_by_id_and_user_id
import time


def get_tweet_by_id(tweet_id):
    """
    get tweet by twitter Id
    :param tweet_id:
    :return:
    """
    try:
        return Tweets.objects.get(tweet_id=tweet_id)
    except Exception:
        return None


def get_tweet_by_id_and_account_id(tweet_id, account_id):
    """
    get tweet by twitter Id
    :param tweet_id:
    :return:
    """
    try:
        return Tweets.objects.get(tweet_id=tweet_id, user__id=account_id)
    except Exception:
        return None


def get_tweets_by_twitter_id(twitter_id):
    try:
        get_user = get_twitter_acc_by_id(twitter_id)
        return get_user.tweets_set.all()
    except Exception:
        return None


def save_tweets(tweets, auth_user_id):
    try:
        if isinstance(tweets, list):
            for tweet in tweets:

                json = tweet._json

                get_tweet = get_tweet_by_id(json['id_str'])
                if json.get("in_reply_to_status_id_str") is not None:
                    save_tweet_reply(json, get_tweet)
                user = json.pop('user')

                if get_tweet is None:
                    getuser = get_twitter_acc_by_id(id=user['id_str'])
                    if getuser:
                        json['user'] = getuser.id
                    else:
                        user["twitter_id"] = user["id_str"]
                        ser = TwitterAccountSerializer(data=user, partial=True)
                        ser.is_valid()
                        user = ser.save()
                        json["user"] = user.id

                if json["place"] is not None:
                    json["location"] = json["place"]["country"]
                json["language"] = json["lang"]
                json['tweet_date'] = str(
                    time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(json['created_at'], '%a %b %d %H:%M:%S +0000 %Y')))
                json['tweet_id'] = json['id_str']
                json['media_url'] = json['entities']['media'][0]['media_url_https'] if 'media' in json[
                    'entities'] else ""

                serializer = TweetsSerializer(data=json, instance=get_tweet, partial=True)
                if serializer.is_valid(raise_exception=True):
                    instance = serializer.save()
                    if "user_mentions" in json["entities"].keys():
                        mentions = json["entities"].pop("user_mentions", None)
                        for mention in mentions:
                            if get_twitter_acc_by_id(id=mention.get("id_str")):
                                Mention.objects.get_or_create(tweet=instance, twitter_id=mention.get("id_str"), mention_date=json['tweet_date'])

        else:
            json = tweets
            user = json.pop('user')
            getuser = get_twitter_acc_by_id_and_user_id(user["id_str"], auth_user_id)

            get_tweet = get_tweet_by_id_and_account_id(json['id_str'], getuser.id if getuser else None)

            if get_tweet is None:

                if getuser:
                    json['user'] = getuser.id
                # else:
                #     user["twitter_id"] = user["id_str"]
                #     ser = TwitterAccountSerializer(data=user, partial=True)
                #     ser.is_valid()
                #     user = ser.save()
                #     json["user"] = user.id
            if json["place"] is not None:
                json["location"] = json["place"]["country"]
            json["language"] = json["lang"]
            json['tweet_date'] = str(
                time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(json['created_at'], '%a %b %d %H:%M:%S +0000 %Y')))
            json['tweet_id'] = json['id_str']
            json['media_url'] = json['entities']['media'][0]['media_url_https'] if 'media' in json[
                'entities'] else ""

            serializer = TweetsSerializer(data=json, instance=get_tweet, partial=True)
            if serializer.is_valid(raise_exception=True):
                instance = serializer.save()

                if "user_mentions" in json["entities"].keys():
                    mentions = json["entities"].pop("user_mentions", None)
                    for mention in mentions:
                        if get_twitter_acc_by_id_and_user_id(mention.get("id_str"), auth_user_id):
                            Mention.objects.get_or_create(tweet=instance, twitter_id=mention.get("id_str"), mention_date=json['tweet_date'])
    except Exception as exc:
        print(f"{exc} exc")