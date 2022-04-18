from django.db import models
from djutil.models import TimeStampedModel
from webapp.base import choices, constants
from django.contrib.postgres.fields import ArrayField
# Create your models here.


class LinkedinAccount(TimeStampedModel):
    user_id = models.CharField(max_length=100)
    linkedin_id = models.CharField(max_length=100, null=True)
    access_token = models.CharField(max_length=300)
    access_token_secret = models.CharField(max_length=300, null=True, blank=True)


class Page(TimeStampedModel):
    user_id = models.CharField(max_length=100)
    page_id = models.CharField(max_length=100)
    name = models.CharField(max_length=100, null=True, blank=True)
    access_token = models.TextField(null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    website = models.CharField(max_length=100, null=True, blank=True)
    about = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    cover_url = models.CharField(max_length=100, null=True, blank=True)
    picture_url = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=20, default="active")
    last_sync_time = models.DateTimeField(blank=True, null=True)
    message = models.CharField(max_length=200, blank=True, null=True)
    sync_status = models.CharField(max_length=7, default=constants.PENDING, choices=choices.STATUS_CHOICES)

    def get_page_urn(self):
        return f"urn:li:organization:{self.page_id}"

    def __str__(self):
        return f"{self.page_id} - {self.name}"


class PageStats(TimeStampedModel):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, null=True)
    shareCount = models.IntegerField()
    uniqueImpressionsCount = models.IntegerField()
    clickCount = models.IntegerField()
    engagement = models.FloatField()
    shareMentionsCount = models.IntegerField()
    likeCount = models.IntegerField()
    impressionCount = models.IntegerField()
    commentMentionsCount = models.IntegerField()
    commentCount = models.IntegerField()
    followerCount = models.IntegerField(default=0)

    def __str__(self):
        return self.page.name


class PostStats(TimeStampedModel):
    page = models.ForeignKey(Page, on_delete=models.CASCADE)
    urn = models.CharField(max_length=100)
    shareCount = models.IntegerField(default=0)
    clickCount = models.IntegerField(default=0)
    engagement = models.FloatField(default=0.0)
    likeCount = models.IntegerField(default=0)
    impressionCount = models.IntegerField(default=0)
    commentCount = models.IntegerField(default=0)
    text = models.CharField(max_length=100)
    post_date = models.DateTimeField(null=True, blank=True)
    media = ArrayField(models.CharField(max_length=200), null=True, blank=True)

    class Meta:
        ordering = ("-post_date",)

    def __str__(self):
        return self.page.name


class PageStatsByDay(TimeStampedModel):
    page = models.ForeignKey(Page, on_delete=models.CASCADE)
    shareCount = models.IntegerField()
    clickCount = models.IntegerField()
    engagement = models.FloatField()
    likeCount = models.IntegerField()
    impressionCount = models.IntegerField()
    commentCount = models.IntegerField()
    stats_date = models.DateField()

