from django.db import models
from django.contrib.postgres.fields import JSONField
from webapp.apps.base.models import BaseModel

# New Schema below
PAGE_TYPE = (
    ("facebook", "facebook"),
    ("instagram", "instagram"),
    ("linkedin", "linkedin"),
    ("twitter", "twitter"),
)

OBJECT_TYPE = (
    ("page", "page"),
    ("post", "post"),
    ("video", "video"),
    ("message", "message"),
)

PENDING = "pending"
SYNC_STATUS = ((PENDING, PENDING), ("progress","progress"),("ok", "ok"), ("failed", "failed"))
PAGE_STATUS = (("active", "active"), ("deleted", "deleted"), ("revoked", "revoked"))

VAL_TYPES = (
    ("int", "int"),
    ("float", "float"),
    ("str", "str"),
    ("dict", "dict"),
    ("json", "json"),
)


class Metrics(BaseModel):
    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    metric = models.CharField(max_length=255)  # platform specific metric name
    slug = models.CharField(max_length=255)
    platform = models.CharField(max_length=20, choices=PAGE_TYPE)
    fields = JSONField(default=dict)

    def __str__(self):
        return self.platform + ":" + self.slug


class MetricsAttribute(BaseModel):
    metrics = models.ForeignKey(Metrics, on_delete=models.CASCADE, db_index=True)
    breakdown = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    aggregration = models.CharField(max_length=255, null=True, blank=True)
    ref_metric = models.ForeignKey(
        Metrics,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        db_index=True,
        related_name="ref_metric_attribute",
    )

    def __str__(self):
        return self.metrics.metric


class Account(BaseModel):
    user_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    page_id = models.CharField(max_length=255, db_index=True)
    type = models.CharField(max_length=20, choices=PAGE_TYPE)
    name = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=PAGE_STATUS)
    token = models.TextField(blank=True)
    token_secret = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True)
    data = JSONField(null=True, blank=True)
    last_synced = models.DateTimeField(null=True, blank=True)
    sync_completed = models.DateTimeField(null=True, blank=True)
    sync_status = models.CharField(max_length=10, default=PENDING, choices=SYNC_STATUS)
    error = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.user_id}"

    class Meta:
        unique_together = ("user_id", "page_id")


# this can be post, video and other media
class AccountObject(BaseModel):
    object_id = models.CharField(max_length=255)
    object_type = models.CharField(max_length=10, choices=OBJECT_TYPE, db_index=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, db_index=True)
    title = models.TextField(blank=True)
    description = models.TextField(null=True, blank=True)
    data = JSONField(null=True, blank=True)
    date_posted = models.DateTimeField(null=True)

    def __str__(self):
        return self.object_id


class TwitterMention(BaseModel):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    mention_id = models.CharField(
        max_length=255
    )  # tweet or reply id where user is mentioned
    date = models.DateTimeField(null=True)
    data = JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.account} - {self.mention_id}"


class TwitterReply(BaseModel):
    reply_id = models.CharField(max_length=255)
    account = models.ForeignKey(
        Account, on_delete=models.CASCADE, null=True, blank=True
    )
    object_id = models.ForeignKey(
        AccountObject, on_delete=models.CASCADE, null=True, blank=True
    )
    is_quote_status = models.CharField(
        max_length=10,
        choices=(("true", "true"), ("false", "false")),
        null=True,
        blank=True,
    )
    retweeted = models.CharField(
        max_length=10,
        choices=(("true", "true"), ("false", "false")),
        null=True,
        blank=True,
    )
    description = models.TextField(null=True, blank=True)
    data = JSONField(null=True, blank=True)
    date_posted = models.DateTimeField(null=True)

    def __str__(self):
        return self.reply_id


class AccountMetrics(BaseModel):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, db_index=True)
    metrics = models.ForeignKey(Metrics, on_delete=models.CASCADE, db_index=True)
    object_id = models.ForeignKey(
        AccountObject, on_delete=models.CASCADE, null=True, blank=True
    )
    reply = models.ForeignKey(
        TwitterReply, on_delete=models.CASCADE, null=True, blank=True
    )
    date = models.DateTimeField(null=True)
    value_type = models.CharField(max_length=255, choices=VAL_TYPES)
    value = models.TextField()

    def __str__(self):
        return self.metrics.metric + ":" + str(self.date) + ":" + self.value


class AccountInbox(BaseModel):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, db_index=True)
    author = models.CharField(max_length=255)
    message = models.TextField(blank=True)
    date = models.DateTimeField(null=True)
    fields = JSONField(null=True, blank=True)

class PostComments(BaseModel):
    comment_id = models.CharField(max_length=255)
    object = models.ForeignKey(AccountObject, on_delete=models.CASCADE, db_index=True)
    author = models.CharField(max_length=255, blank=True, null=True)
    message = models.TextField(blank=True)
    date = models.DateTimeField(null=True)
    fields = JSONField(null=True, blank=True)

    def __str__(self):
        return self.comment_id

class CommentReplies(BaseModel):
    reply_id = models.CharField(max_length=255)
    comment = models.ForeignKey(PostComments, on_delete=models.CASCADE, db_index=True)
    author = models.CharField(max_length=255, blank=True, null=True)
    message = models.TextField(blank=True)
    date = models.DateTimeField(null=True)
    fields = JSONField(null=True, blank=True)

    def __str__(self):
        return self.reply_id


