import time
from datetime import datetime
from django.db.models import Q
from tweepy import TweepError
from webapp.apps.metrics.data_loader import InputDataLoader
from webapp.apps.metrics.models import (
    Account,
    AccountObject,
    AccountMetrics,
    TwitterReply,
    TwitterMention,
    AccountInbox)
import logging

log = logging.getLogger("twitter")


class TwitterDataLoader(InputDataLoader):
    def  __init__(self, user_id, page_id):
        self.user_id = user_id
        self.page_id = page_id
        
    def save_page(self, data):
        page, c = Account.objects.get_or_create(
            type="twitter", page_id=self.page_id, user_id=self.user_id
        )
        data_dict = {}
        page.name = data.get("screen_name")
        page.status = data.get("status")
        page.token = data.get("access_token")
        page.token_secret = data.get("access_token_secret")
        if data.get("picture_url"):
            data_dict.update({"profile_pic_url": data.get("picture_url")})
            page.data = data_dict
        now = datetime.now()
        page.last_synced = now.strftime('%Y-%m-%d %H:%M:%S')
        page.save()
        return c

    def fetch_metrics(self):
        page = Account.objects.get(page_id=self.page_id, user_id=self.user_id)
        try:
            self.fetch_messages()
        except Exception as err:
            self.flag = False
            page.sync_status = "failed"
            page.error = "message" + str(err)
            page.save()

        try:
            self.fetch_post()
        except Exception as err:
            self.flag = False
            page.sync_status = "failed"
            page.error = "post" + str(err)
            page.save()
        try:
            self.fetch_account_insights()
        except Exception as err:
            update = ["sync_status", "error"]
            if isinstance(err, TweepError):
                # if err.api_code == 89:
                page.status = "revoked"
                update.append("status")
            self.flag = False
            page.sync_status = "failed"
            page.error = "insight" + str(err)
            page.save(update_fields=update)

        if self.flag:
            page.sync_status = "ok"
            page.error = ""
            page.save()
        return page

    def fetch_account_insights(self):
        extracted_insights = {}
        metrics = self.get_metrics(type="twitter")
        account = self.get_page(page_id=self.page_id, user_id=self.user_id)
        api = self.connect_twitter_api(
            access_token=account.token, access_token_secret=account.token_secret
        )
        response = api.get_user(user_id=self.page_id)
        response = response._json
        tweet_count = account.accountobject_set.filter(object_type="post").count()

        mention_count = account.twittermention_set.count()
        extracted_insights.update(
            {
                "followers_count": response["followers_count"],
                "favourites_count": response["favourites_count"],
                # "friends_count": response["friends_count"],
                # "tweets_count": tweet_count,
                # "mention": mention_count
            }
        )
        create_objects = []
        update_objects = []
        for metric, value in extracted_insights.items():
            try:
                o = AccountMetrics.objects.get(
                    account=account, metrics_id=metrics[metric], date=None,
                    object_id=None, reply=None,
                )
                o.value = value
                update_objects.append(o)
            except AccountMetrics.DoesNotExist:  # noqa E722
                create_objects.append(
                    AccountMetrics(
                        account=account,
                        metrics_id=metrics[metric],
                        value_type=type(value).__name__,
                        value=value,
                    )
                )
            except Exception as e:
                log.info("insight", str(e))
        AccountMetrics.objects.bulk_create(create_objects)

    def fetch_messages(self):
        account = self.get_page(page_id=self.page_id, user_id=self.user_id)
        api = self.connect_twitter_api(
            access_token=account.token, access_token_secret=account.token_secret
        )
        messages = api.list_direct_messages()
        #create_objects = []
        #update_objects = []
        for message in messages:
            if message.message_create["target"]["recipient_id"] == account.page_id:
                json = message.__dict__
                ### code by shyam - to update existing and create new message
                AccountInbox.objects.get_or_create(
                    account=account,
                    author=json["message_create"]['sender_id'],
                    date=time.strftime(
                                "%Y-%m-%d %H:%M:%S",
                                time.gmtime(int(json["created_timestamp"]) / 1000.0),
                            ),
                    defaults={"message": json["message_create"]["message_data"]["text"],
                              "fields": {"from": json["message_create"]['sender_id']}},
                )
                ### End - commented the below logic because get query doesn't identify the message uniquely
        #         try:
        #             o = AccountInbox.objects.get(
        #                 account=account,
        #                 author=json["message_create"]['sender_id']
        #             )
        #             o.message = message["message_create"]["message_data"]["text"]
        #             update_objects.append(o)
        #         except AccountInbox.DoesNotExist:  # noqa E722
        #             create_objects.append(
        #                 AccountInbox(
        #                     account=account,
        #                     author=json["message_create"]['sender_id'],
        #                     message=json["message_create"]["message_data"]["text"],
        #                     date=time.strftime(
        #                         "%Y-%m-%d %H:%M:%S",
        #                         time.gmtime(int(json["created_timestamp"]) / 1000.0),
        #                     ),
        #                 )
        #             )
        # AccountInbox.objects.bulk_create(create_objects)
        # AccountInbox.objects.bulk_update(update_objects, ["message"])

    def fetch_post(self):
        account = self.get_page(page_id=self.page_id, user_id=self.user_id)
        metrics = self.get_metrics(type="twitter")
        api = self.connect_twitter_api(
            access_token=account.token, access_token_secret=account.token_secret
        )
        tweets = api.user_timeline(count=200)
        tweets_metrics = self.save_tweet_reply(tweets)
        reply = api.mentions_timeline(count=200)
        reply_metrics = self.save_tweet_reply(reply)
        extracted_metrics = tweets_metrics + reply_metrics
        create_objects = []
        update_objects = []
        for extract in extracted_metrics:
            post = reply = None
            if extract["type"] == "post":
                post = self.post_exists(account=account, object_id=extract["id"])
            else:
                reply = self.reply_exists(account=account, object_id=extract["id"])
            if post or reply:
                for metric, value in extract.items():
                    if metric in metrics.keys():
                        try:
                            o = AccountMetrics.objects.get(
                                Q(
                                    account=account,
                                    metrics_id=metrics[metric],
                                    date=None,
                                )
                                & (Q(object_id=post) & Q(reply=reply))
                            )
                            o.value = value
                            update_objects.append(o)
                        except:  # noqa E722
                            create_objects.append(
                                AccountMetrics(
                                    account=account,
                                    metrics_id=metrics[metric],
                                    value_type=type(value).__name__,
                                    value=value,
                                    object_id=post,
                                    reply=reply,
                                )
                            )
        AccountMetrics.objects.bulk_create(create_objects)
        AccountMetrics.objects.bulk_update(update_objects, ["value"])

    def post_exists(self, account, object_id):
        try:
            return AccountObject.objects.get(
                object_type="post", account=account, object_id=object_id
            )
        except Exception as e:
            return None

    def reply_exists(self, account, object_id):
        try:
            return TwitterReply.objects.get(account=account, reply_id=object_id)
        except:  # noqa E722
            return None

    def save_tweet_reply(self, object):
        account = self.get_page(page_id=self.page_id, user_id=self.user_id)
        create_objects = {"post": [], "mentions": [], "reply": []}
        update_objects = {"post": [], "reply": []}
        extracted_metrics = []
        for tweet in list(object):

            json = tweet._json
            user = json.pop("user")
            # if account.page_id == user["id_str"]:

            object_type = (
                "post" if json["in_reply_to_status_id_str"] is None else "reply"
            )
            metrics = {
                "id": json["id_str"],
                "type": object_type,
                "retweet_count": json["retweet_count"],
                "favourites_count": json["favorite_count"],
            }
            extracted_metrics.append(metrics)
            media = []
            if "media" in json["entities"]:
                for m in json["entities"]["media"]:
                    media.append(m["media_url_https"])
            # save post
            if object_type == "post" and account.page_id == user["id_str"]:
                # print(json["id_str"])
                try:
                    o = AccountObject.objects.get(
                        account=account, object_id=json["id_str"], object_type="post"
                    )
                    o.description = json["text"]
                    update_objects["post"].append(o)
                except AccountObject.DoesNotExist:  # noqa E722
                    json_data = {
                        "author": user["screen_name"],
                        "retweeted": json["retweeted"],
                        "is_quote_status": json["is_quote_status"],
                        "media": media
                    }
                    create_objects["post"].append(
                        AccountObject(
                            account=account,
                            object_id=json["id_str"],
                            object_type="post",
                            title=json["text"],
                            date_posted=str(
                                time.strftime(
                                    "%Y-%m-%d %H:%M:%S",
                                    time.strptime(
                                        json["created_at"], "%a %b %d %H:%M:%S +0000 %Y"
                                    ),
                                )
                            ),
                            data=json_data,
                        )
                    )
            elif object_type == "reply":
                # print(json["id_str"])
                if account.page_id == user["id_str"]:
                    reply_account = account
                else:
                    reply_account = None
                post_exists = self.post_exists(
                    account=account, object_id=json["in_reply_to_status_id_str"]
                )
                if post_exists:
                    try:
                        o = TwitterReply.objects.get(
                            account=reply_account,
                            reply_id=json["id_str"],
                            # object_id=post_exists,
                        )
                        o.object_id = post_exists
                        o.description = json["text"]
                        update_objects["reply"].append(o)
                    except TwitterReply.DoesNotExist:  # noqa E722
                        json_data = {
                            "author": user["screen_name"],
                            "retweeted": json["retweeted"],
                            "is_quote_status": json["is_quote_status"],
                            "media": media
                        }
                        create_objects["reply"].append(
                            TwitterReply(
                                account=reply_account,
                                object_id=post_exists,
                                reply_id=json["id_str"],
                                description=json["text"],
                                date_posted=str(
                                    time.strftime(
                                        "%Y-%m-%d %H:%M:%S",
                                        time.strptime(
                                            json["created_at"],
                                            "%a %b %d %H:%M:%S +0000 %Y",
                                        ),
                                    )
                                ),
                                data=json_data,
                            )
                        )
            if "user_mentions" in json["entities"].keys():
                mentions = json["entities"].pop("user_mentions", None)
                for mention in mentions:
                    if mention.get("id_str") == account.page_id:
                        data = {
                            "author": user["screen_name"],
                            "media": media,
                            "title": json["text"]
                        }
                        try:
                            o = TwitterMention.objects.get(
                                account=account, mention_id=json["id_str"]
                            )
                        except TwitterMention.DoesNotExist:  # noqa E722
                            create_objects["mentions"].append(
                                TwitterMention(
                                    account=account, mention_id=json["id_str"],
                                    data=data,
                                    date=str(
                                    time.strftime(
                                        "%Y-%m-%d %H:%M:%S",
                                        time.strptime(
                                            json["created_at"],
                                            "%a %b %d %H:%M:%S +0000 %Y",
                                        ),
                                    )
                                )
                                )
                            )
        TwitterMention.objects.bulk_create(create_objects["mentions"])
        AccountObject.objects.bulk_create(create_objects["post"])
        AccountObject.objects.bulk_update(update_objects["post"], ["description"])
        TwitterReply.objects.bulk_create(create_objects["reply"])
        TwitterReply.objects.bulk_update(update_objects["reply"], ["description", "object_id"])
        return extracted_metrics
