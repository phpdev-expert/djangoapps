from django.contrib import admin

# Register your models here.
from webapp.apps.base.admin import CustomModelAdmin
from webapp.apps.twitter import models

# Register your models here.


@admin.register(models.TwitterAccount)
class AdminTwitterAccount(CustomModelAdmin):
    """
    Twitter Account Admin
    """
    list_display = [
        'auth_user_id',
        'twitter_id',
        'screen_name',
    ]
    search_fields = ['auth_user_id', 'twitter_id', 'screen_name']


@admin.register(models.DirectMessages)
class AdminDirectMessages(CustomModelAdmin):
    """
    Direct message Admin
    """
    list_display = [
        'message_id',
        'text'
    ]
    search_fields = ['message_id']


@admin.register(models.Tweets)
class AdminTweets(CustomModelAdmin):
    """
    Account Tweets Admin
    """
    list_display = [
        "user",
        'tweet_id',
        'text'
    ]
    search_fields = ['tweet_id']


@admin.register(models.TweetReply)
class AdminTweetReply(CustomModelAdmin):
    """
    Account Tweet Replies Admin
    """
    list_display = [
        'reply_id',
        "user",
        'text',
        'tweet_id'
    ]
    search_fields = ['reply_id']


@admin.register(models.Mention)
class AdminMention(CustomModelAdmin):
    """
    Account Mention Admin
    """
    list_display = [
        'twitter_id',
        'reply',
        'tweet',

    ]
    search_fields = ['twitter_id']