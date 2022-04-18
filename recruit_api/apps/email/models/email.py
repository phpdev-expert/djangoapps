from django.db import models
from model_utils.models import TimeStampedModel
from .recipient import EmailRecipient


class Email(TimeStampedModel):
    subject = models.CharField(max_length=255)
    message = models.TextField(blank=True, null=True)
    # may be in future we may have multiple server, so to track that adding email_from
    email_from = models.EmailField()
    recipients = models.ManyToManyField(EmailRecipient, related_name='recipient_email')

    class Meta:
        app_label = "email"
        verbose_name_plural = "Email"

    def __str__(self):
        return self.subject
