from webapp.apps.twitter.models import Tweets, TweetReply, Mention, TwitterAccount
from webapp.apps.twitter.serializers.tweet_reply_serializer import TweetReplySerializer
from webapp.apps.twitter.serializers.twitter_account_serializer import TwitterAccountSerializer
from webapp.apps.twitter.services.twitter_account import get_twitter_acc_by_id, get_twitter_acc_by_id_and_user_id
import time


def get_tweet_reply_by_id(id):
    try:
        return TweetReply.objects.get(reply_id=id)
    except Exception:
        return None


def get_tweet_reply_by_id_and_tweet_id(id, tweet_id=None):
    try:
        return TweetReply.objects.get(reply_id=id, tweet_id__id=tweet_id)
    except Exception:
        return None


def get_tweet_reply_by_id_and_user_id(id, auth_user_id=None):
    try:
        return TweetReply.objects.get(reply_id=id, user__auth_user_id=auth_user_id)
    except Exception:
        return None


def save_tweet_reply(reply, tweet, auth_user_id):
    json = reply
    try:
        user = json.pop('user')
        getuser = get_twitter_acc_by_id_and_user_id(user['id_str'], auth_user_id)
        get_reply = get_tweet_reply_by_id_and_user_id(json['id_str'], auth_user_id)
        if tweet:   # saved in my db
            get_reply = get_tweet_reply_by_id_and_tweet_id(json['id_str'], tweet.id)
            json['tweet_id'] = tweet.id
        else:
            reply = get_tweet_reply_by_id_and_user_id(json['in_reply_to_status_id_str'], auth_user_id)
            reply_none = TweetReply.objects.filter(reply_id=json['in_reply_to_status_id_str'], user=None, tweet_id=None)
            if reply:   # my reply parent
                json["parent"] = reply.id
            elif reply_none.exists():
                json["parent"] = reply_none.get().id

        if not get_reply:
            reply_exist = TweetReply.objects.filter(reply_id=json['id_str'], user=None, tweet_id=None)
            if reply_exist.exists():
                get_reply = reply_exist.get()
            else:
                json['reply_id'] = json['id_str']
                json['twitter_id'] = user['id_str']

        if getuser is not None:
            json.update({"user": getuser.id})
        # else:
        #     user["twitter_id"] = user["id_str"]
        #
        #     instance = get_twitter_acc_by_id_and_user_id(user["id_str"])
        #     ser = TwitterAccountSerializer(instance=instance, data=user, partial=True)
        #     ser.is_valid(raise_exception=True)
        #     user = ser.save()
        #     json.update({"user": user.id})
        if json["place"] is not None:
            json["location"] = json["place"]["country"]
        json["language"] = json["lang"]
        json['reply_date'] = time.strftime('%Y-%m-%d %H:%M:%S',
                                           time.strptime(json['created_at'], '%a %b %d %H:%M:%S +0000 %Y'))
        json['media_url'] = json['entities']['media'][0]['media_url_https'] if 'media' in json['entities'] else ""
        serializer = TweetReplySerializer(data=json, instance=get_reply, partial=True)
        if serializer.is_valid(raise_exception=True):
            instance = serializer.save()
            if "user_mentions" in json["entities"].keys():
                mentions = json["entities"].pop("user_mentions", None)
                for mention in mentions:
                    if get_twitter_acc_by_id_and_user_id(mention.get("id_str"), auth_user_id):
                        Mention.objects.get_or_create(reply=instance, twitter_id=mention.get("id_str"),
                                                      mention_date=json['reply_date'])

    except Exception as exc:
        print("services error {}: ".format(exc))
