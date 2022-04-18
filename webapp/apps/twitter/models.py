from djutil.models import TimeStampedModel
from django.db import models


# Create your models here.


class TwitterAccount(TimeStampedModel):
    PENDING = 'pending'
    OK = 'ok'
    FAILED = 'failed'
    STATUS_CHOICES = (
        (PENDING, 'pending'),
        (OK, 'ok'),
        (FAILED, 'failed')
    )
    auth_user_id = models.CharField(max_length=100, null=True, blank=True)
    twitter_id = models.CharField(max_length=100)
    access_token = models.CharField(max_length=200, blank=True, null=True)
    access_token_secret = models.CharField(max_length=200, blank=True, null=True)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    screen_name = models.CharField(max_length=100, null=True, blank=True)
    location = models.CharField(max_length=100, blank=True)
    language = models.CharField(max_length=100, blank=True)
    followers_count = models.IntegerField(default=0)
    friends_count = models.IntegerField(default=0)
    favourites_count = models.IntegerField(default=0)
    account_type = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=100, null=True, blank=True)
    last_sync_time = models.DateTimeField(blank=True, null=True)
    sync_status = models.CharField(max_length=7, default=PENDING, choices=STATUS_CHOICES)
    message = models.CharField(max_length=200, blank=True, null=True)
    
    def __str__(self):
        return "{} - {}".format(self.screen_name, self.auth_user_id)


class Tweets(TimeStampedModel):
    user = models.ForeignKey(TwitterAccount, on_delete=models.CASCADE, null=True)
    tweet_id = models.CharField(max_length=100)
    tweet_date = models.DateTimeField(null=True)
    text = models.TextField(max_length=200)
    media_url = models.CharField(max_length=200, default="", blank=True)
    retweet_count = models.IntegerField(default=0)
    favourite_count = models.IntegerField(default=0)
    is_quote_status = models.BooleanField(default=False)
    retweeted = models.BooleanField(default=False)
    location = models.CharField(max_length=100, blank=True)
    language = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ("-tweet_date",)

    def __str__(self):
        return "{} - {}".format(self.tweet_id, self.user.auth_user_id if self.user else None)


class TweetReply(TimeStampedModel):
    user = models.ForeignKey(TwitterAccount, on_delete=models.CASCADE, null=True)
    reply_id = models.CharField(max_length=100)
    twitter_id = models.CharField(max_length=100)
    tweet_id = models.ForeignKey(Tweets, on_delete=models.CASCADE, null=True, blank=True)
    text = models.TextField()
    media_url = models.CharField(max_length=200, default="", blank=True)
    reply_date = models.DateTimeField(null=True)
    retweet_count = models.IntegerField(default=0)
    favourite_count = models.IntegerField(default=0)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    location = models.CharField(max_length=100, blank=True)
    language = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ("-reply_date",)

    def __str__(self):
        id = None
        if self.user:
            id = self.user.auth_user_id
        elif self.tweet_id:
            id = self.tweet_id.user.auth_user_id
        return "{} - {}".format(self.reply_id, id)


class DirectMessages(TimeStampedModel):
    message_id = models.CharField(max_length=100, unique=True)
    sender_id = models.CharField(max_length=100)
    receiver_id = models.CharField(max_length=100)
    text = models.TextField()
    message_date = models.DateTimeField(null=True)

    def __str__(self):
        return "{}".format(self.message_id)

    class Meta:
        ordering = ("-message_date",)


class Mention(TimeStampedModel):
    tweet = models.ForeignKey(Tweets, on_delete=models.CASCADE, null=True)
    reply = models.ForeignKey(TweetReply, on_delete=models.CASCADE, null=True)
    twitter_id = models.CharField(max_length=100)
    mention_date = models.DateTimeField(null=True)

    class Meta:
        ordering = ("-mention_date",)


